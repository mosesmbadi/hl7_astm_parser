"""
HL7 v2 results (ORU^R01, OUL^R22) -> runs of results for EasyMed.

Analyzers differ in where they put things; see docs/Equipment Docs:

                  sample ID              one OBR per   value          separators
  HumaCount 30TS  SAC-3, else MSH-10     sample        OBX-5          $~\\&  ($ = components)
  Dymind 5-part   OBR-3                  sample        OBX-5          ^~\\&
  Maglumi X8      SPM-2.1                test          OBX-5.1/5.2    ^~\\&, OBX-2 empty

So separators are read from MSH, and results are grouped by sample, not by
OBR.
"""
import re

# Histograms and scattergrams come as one long hex string per OBX. They are
# pictures, not results, and are never posted.
HISTOGRAM_VALUE = re.compile(r'[0-9A-Fa-f]{64,}')
# Histogram metadata on the HumaCount (scale and discriminator channels).
HISTOGRAM_META = re.compile(r'.*\bSCALE$|[WRPE]Marker\d+$', re.IGNORECASE)
# OBX value types that are never results: IS analyzer settings (Take Mode,
# Blood Mode...), ED embedded data (images).
NOT_RESULTS = {'IS', 'ED'}


def is_reportable(code, value):
    if not code or not value:
        return False
    # Analyzers send '**.*' style masks when a value couldn't be measured
    if re.fullmatch(r'[*.\-]+', value):
        return False
    return not HISTOGRAM_VALUE.fullmatch(value) and not HISTOGRAM_META.fullmatch(code)


class Separators:
    def __init__(self, msh):
        # MSH|^~\&|... : MSH-1 is the field separator, MSH-2 the rest
        self.field_sep = msh[3] if len(msh) > 3 else '|'
        encoding = msh[4:8] if len(msh) > 4 else '^~\\&'
        self.component_sep = encoding[0] if len(encoding) > 0 else '^'
        self.repetition_sep = encoding[1] if len(encoding) > 1 else '~'

    def components(self, value):
        return value.split(self.component_sep)

    def component(self, value, index):
        """The component at index, or the whole field when it has none."""
        parts = self.components(value)
        return (parts[index] if len(parts) > index else parts[0]).strip()

    def first_value(self, value):
        """First non-empty component: Maglumi X8 sends '3.56^' or '^Reactive'."""
        return next((p.strip() for p in self.components(value) if p.strip()), '')

    def text(self, value):
        """'FAMILY^GIVEN' -> 'FAMILY GIVEN'"""
        return " ".join(p.strip() for p in self.components(value) if p.strip())

    def first_repeat(self, value):
        return value.split(self.repetition_sep)[0]


def field(fields, n):
    return fields[n] if len(fields) > n else ""


def convert_hl7_to_json(hl7_str):
    """
    Converts an HL7 result message into one run per sample:

        [{"sender": "HumaCount 30TS", "sample_id": "DDLR00012-2026",
          "patient_name": ..., "patient_id": ...,
          "results": [{"code": "WBC", "value": "5.39", "unit": "10^9/l",
                       "flag": "H", "reference_range": "5.00-11.60"}]}]

    The codes are the analyzer's own; EasyMed maps them to test panels.
    Quality-control runs are left out.
    """
    segments = [s.strip() for s in re.split(r'[\r\n]+', hl7_str.strip()) if s.strip()]

    sep = Separators('MSH|^~\\&')
    runs = {}  # (sample_id, patient_id, patient_name) -> run, in arrival order
    sender = control_id = ""
    patient_name = patient_id = ""
    ids = {}  # candidate sample IDs for the specimen being read
    is_qc = False

    for segment in segments:
        kind = segment[:3]
        if kind == 'MSH':
            sep = Separators(segment)
        fields = segment.split(sep.field_sep)

        if kind == 'MSH':
            # fields[1] is MSH-2 (encoding characters), so MSH-n is fields[n-1]
            sender = sep.component(field(fields, 2), 0)
            control_id = field(fields, 9).strip()
            patient_name = patient_id = ""
            ids, is_qc = {}, False

        elif kind == 'PID':
            patient_id = sep.component(field(fields, 3), 0)
            patient_name = sep.text(field(fields, 5))
            ids, is_qc = {}, False  # a new patient is a new specimen

        elif kind == 'SPM':
            # SPM-2.1 sample ID on the Maglumi X8; SPM-11 'Q' marks QC material
            ids['spm'] = sep.component(field(fields, 2), 0)
            is_qc = field(fields, 11).strip().upper() == 'Q'

        elif kind == 'SAC':
            # SAC-3 container identifier, the sample ID on the HumaCount 30TS
            ids['sac'] = field(fields, 3).strip()

        elif kind == 'OBR':
            # OBR-3 filler number holds the sample ID on Dymind, OBR-2 the
            # placer number. The X8 sends one OBR per test with both empty,
            # so empty values never wipe out an ID already seen.
            for key, n in (('obr3', 3), ('obr2', 2)):
                value = sep.component(field(fields, n), 0)
                if value:
                    ids[key] = value

        elif kind == 'OBX':
            if is_qc or field(fields, 2).strip().upper() in NOT_RESULTS:
                continue
            # OBX-3 is 'LOINC^name^system' on Dymind, a bare name elsewhere
            code = sep.component(field(fields, 3), 1)
            value = sep.first_value(field(fields, 5))
            if not is_reportable(code, value):
                continue

            sample_id = sample_id_of(ids, sender, control_id)
            key = (sample_id, patient_id, patient_name)
            if key not in runs:
                runs[key] = {
                    "sender": sender,
                    "sample_id": sample_id,
                    "patient_name": patient_name,
                    "patient_id": patient_id,
                    "results": [],
                }
            runs[key]["results"].append({
                "code": code,
                "value": value,
                # '$10^9/l' on the 30TS: an empty first component, '$' being
                # its separator. Not split further: '^' can be part of a unit.
                "unit": field(fields, 6).strip().lstrip('$' + sep.component_sep).strip(),
                "reference_range": field(fields, 7).strip(),
                # OBX-8 repeats ('L~A'); the first is the abnormal flag
                "flag": sep.component(sep.first_repeat(field(fields, 8)), 0),
            })

    return list(runs.values())


def sample_id_of(ids, sender, control_id):
    """
    The sample code EasyMed uses to find the patient's tests, from the most
    specific place an analyzer puts it to the least.

    The HumaCount 30TS/80TS manual also puts the sample ID in MSH-10 (message
    control ID); it sends 'AUTO_nnnnn' there when none was entered. Other
    analyzers use MSH-10 for a message number, so it is only read for them.
    """
    found = ids.get('spm') or ids.get('sac') or ids.get('obr3') or ids.get('obr2')
    if found:
        return found
    if 'humacount' in sender.lower() and control_id and not control_id.upper().startswith('AUTO_'):
        return control_id
    return ""
