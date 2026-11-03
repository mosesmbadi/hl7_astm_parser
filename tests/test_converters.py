"""
Run with: python -m pytest tests  (from the repo root)

Messages are shaped like the HumaCount 30TS (README.md, and a run seen in
production), the Dymind sample in src/coms/send_hl7.py, and a HumaStar ASTM
transmission.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from converters.astm_to_json import convert_astm_to_json  # noqa: E402
from converters.hl7_to_json import convert_hl7_to_json  # noqa: E402

HISTOGRAM = '0000000000000000000000656' + '0A' * 60

HUMACOUNT_30TS = "\r".join([
    "MSH|^~\\&|HumaCount 30TS|Human|||20241024152427||ORU^R01|42|P|2.5.1||||||UNICODE UTF-8",
    "PID|||PATIENT_ID001||RUKIA OSMAN||19621119000000|F",
    "SPM|1|||WB|||||||P",
    "SAC|||DDLR00012-2026",
    "OBR|1||5|01001^Automated Count^99MRC||20241024152325",
    "OBX|1|NM|WBC||5.39|$10^9/l|5.00-11.60|",
    "OBX|2|NM|LYM%||48.4|$%|19.1-48.5|",
    "OBX|3|NM|GRA%||42.1|$%|43.6-73.4|L",
    "OBX|4|NM|WBC HISTO||" + HISTOGRAM + "|||",
    "OBX|5|NM|WMarker1||28|fl||",
    "OBX|6|IS|Take Mode||O||||",
]) + "\r"


def test_30ts_sample_id_comes_from_sac_not_the_obr_run_counter():
    [run] = convert_hl7_to_json(HUMACOUNT_30TS)
    assert run['sample_id'] == 'DDLR00012-2026'
    assert run['sender'] == 'HumaCount 30TS'
    assert run['patient_name'] == 'RUKIA OSMAN'


def test_30ts_results_keep_analyzer_codes_and_drop_histograms_and_settings():
    [run] = convert_hl7_to_json(HUMACOUNT_30TS)
    # Histograms, their scales and markers are picture data, not results
    assert [r['code'] for r in run['results']] == ['WBC', 'LYM%', 'GRA%']
    wbc = run['results'][0]
    assert wbc == {'code': 'WBC', 'value': '5.39', 'unit': '10^9/l',
                   'reference_range': '5.00-11.60', 'flag': ''}
    assert run['results'][2]['flag'] == 'L'


def test_no_sample_code_still_delivers_the_results():
    message = HUMACOUNT_30TS.replace("SAC|||DDLR00012-2026", "SAC|||").replace(
        "OBR|1||5|", "OBR|1|||").replace("ORU^R01|42|", "ORU^R01|AUTO_00042|")
    [run] = convert_hl7_to_json(message)
    assert run['sample_id'] == ''
    assert len(run['results']) == 3


def test_dymind_sample_id_comes_from_obr3():
    message = "\r".join([
        "MSH|^~\\&|DF5x|Dymind|||20250116101949||ORU^R01|1|P|2.3.1",
        "PID|1",
        "OBR|1||DDLR00013-2026|01001^Automated Count^99MRC",
        "OBX|1|IS|02001^Take Mode^99MRC||O||||||F",
        "OBX|7|NM|6690-2^WBC^LN||7.10|10*9/L|4.00-10.00|N~A|||F",
        "OBX|8|NM|770-8^NEU%^LN||**.*|%|50.0-70.0|~A|||F",
    ])
    [run] = convert_hl7_to_json(message)
    assert run['sender'] == 'DF5x'
    assert run['sample_id'] == 'DDLR00013-2026'
    assert run['results'] == [{'code': 'WBC', 'value': '7.10', 'unit': '10*9/L',
                               'reference_range': '4.00-10.00', 'flag': 'N'}]


def test_astm_transmission_with_two_patients_gives_two_runs():
    message = "\r".join([
        "H|\\^&|||HumaStar 100^1.0|||||||P|1|20250101",
        "P|1||DDLR00001-2026||ACHIENG OTIENO",
        "O|1||||||||||||||Serum",
        "R|1|^^^CREA|1.02|mg/dl|0.6-1.2|N",
        "P|2||DDLR00002-2026||JUMA ALI",
        "O|1||||||||||||||Serum",
        "R|1|^^^UREA|30|mg/dl|15-45|N",
        "L|1|N",
    ])
    runs = convert_astm_to_json(message)
    assert [(r['sender'], r['sample_id'], r['results'][0]['code']) for r in runs] == [
        ('HumaStar 100', 'DDLR00001-2026', 'CREA'),
        ('HumaStar 100', 'DDLR00002-2026', 'UREA'),
    ]


# ---------------------------------------------------------------------------
# Messages from the manuals and captures in docs/Equipment Docs
# ---------------------------------------------------------------------------

DOCS = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Equipment Docs')

# HC30_80TS_LISInterfaceManual_V5, 5.2.1: '$' is the component separator, no
# SAC, and the sample ID (here none entered) is in MSH-10.
HUMACOUNT_80TS_MANUAL = "\r".join([
    "MSH|$~\\&|Humacount 80TS||||20150121110514||ORU_R01|AUTO_00000|P|2.5.1||||||UNICODE UTF-8|||",
    "PID|||||||00000000|U",
    "NTE|1",
    "NTE|2||32",
    "OBR||||Humacount 80TS",
    "SPM|1|||WB|||||||P",
    "OBX|1|TX|WBC||2.39|$10^9/l|4.00-11.70|L|||P",
    "OBX|9|TX|HGB||7.3|$g/dl|8.8-16.5|L|||P",
    "OBX|23|TX|WBC SCALE||400|$fl|||||P",
    "OBX|24|TX|WMarker1||19||||||P",
    "OBX|27|TX|WBC HISTO||" + HISTOGRAM + "||||||P",
])


def test_humacount_manual_message_reads_dollar_separated_units():
    [run] = convert_hl7_to_json(HUMACOUNT_80TS_MANUAL)
    assert run['sender'] == 'Humacount 80TS'
    assert run['sample_id'] == ''  # AUTO_00000: no sample ID was entered
    assert run['results'] == [
        {'code': 'WBC', 'value': '2.39', 'unit': '10^9/l', 'reference_range': '4.00-11.70', 'flag': 'L'},
        {'code': 'HGB', 'value': '7.3', 'unit': 'g/dl', 'reference_range': '8.8-16.5', 'flag': 'L'},
    ]


def test_humacount_sample_id_in_msh10():
    [run] = convert_hl7_to_json(HUMACOUNT_80TS_MANUAL.replace('AUTO_00000', 'S0012'))
    assert run['sample_id'] == 'S0012'


# Maglumi_X8_LIS_HL7, 6.3.2: OUL^R22, sample ID in SPM-2.1, one OBR per test,
# OBX-2 empty, value in OBX-5.1 (5.2 for text). The manual's third OBX says
# TG; it is the TSH result.
MAGLUMI_X8_MANUAL = "\r".join([
    "MSH|^~\\&|X8||LIS||20191025105016||OUL^R22|201910251050161|P|2.5|||NE|NE||UTF-8",
    "PID|1||10011012||Li Mu||19960222|1||||||||||||||Han||||||China||||||||||23^1",
    "PV1|1|Outpatient|Internal Medicine^201^10^Second Facility||||Wang Miao",
    "SPM|1|20251122553^1523^^N0002^2||1|||||||P|||Yao An^Wang Yang^^^|||20191021112250|20191021122250",
    "ORC|RF||||||2||20190124102516|||Wang Miao",
    "OBR|1|||FT3",
    "OBX|1||FT3||3.56^|mmol/L|1.23-5.25|N|||F|||20191021112250||Zhang Shun^Li Xiao||Module1^X8|20191021212250",
    "NTE|1",
    "OBR|2|||TG",
    "OBX|2||TG||20^|mmol/L|30-100|L|||F|||20191021112250||Zhang Shun^Li Xiao||Module1^X8|20191021212250",
    "NTE|2",
    "OBR|3|||TSH",
    "OBX|3||TSH||^Reactive|mmol/L|6-8.5|H|||F|||20191021112250||Zhang Shun^Li Xiao||Module1^X8|20191021212250",
])


def test_maglumi_x8_results_are_one_sample_from_spm():
    [run] = convert_hl7_to_json(MAGLUMI_X8_MANUAL)
    assert (run['sender'], run['sample_id'], run['patient_name']) == ('X8', '20251122553', 'Li Mu')
    assert [(r['code'], r['value'], r['flag']) for r in run['results']] == [
        ('FT3', '3.56', 'N'), ('TG', '20', 'L'), ('TSH', 'Reactive', 'H')]


def test_maglumi_x8_qc_is_not_sent():
    qc = "\r".join([
        "MSH|^~\\&|X8||LIS||20191025105016||OUL^R22|201910251050161|P|2.5|||NE|NE||UTF-8",
        "SPM|1|Bole^65318^1001^N0002^2|||||||||Q",
        "OBR|1||| FT3",
        "OBX|1|| FT3||3.56^|mmol/L|||||F||||||| Module1^X8|20191021154122",
    ])
    assert convert_hl7_to_json(qc) == []


def test_humastar_100_capture():
    with open(os.path.join(DOCS, 'sample_data_from_hm100.txt'), encoding='utf-8') as handle:
        [run] = convert_astm_to_json(handle.read())
    assert (run['sender'], run['sample_id']) == ('HS100x', '214226')
    assert run['results'] == [
        {'code': 'CREA', 'value': '0.96', 'unit': 'mg / dL', 'reference_range': '', 'flag': ''},
        {'code': 'UREA', 'value': '34.9', 'unit': 'mg / dL', 'reference_range': '', 'flag': ''},
    ]


def test_humastar_not_measured_and_qc_are_not_sent():
    # HumaStar100_200_300SR manual 2.8.2 and 2.8.5
    message = "\r".join([
        "H|\\^&|||HS300SR^V1.0|||||Host||P|1|20190607134056",
        " P|1||0000000001||0000000001|||MALE|||||||||||||||||||||||||",
        "  O|1|||GOT|False||||||||||Serum|||||||||||||||",
        "   R|1|GOT||U / l||||125.0||||20190607134012|",
        "  O|2|||Alb|False||||||||||Serum|||||||||||||||",
        "   R|1|Alb||g/dl||||-99000000000||||00010101000000|",
        " P|2||Serodos-00000004||Serodos-00000004|||Control|||||||||||||||||||||||||",
        "  O|1|||GOT|False||||||||||Serum|||||||||||||||",
        "   R|1|GOT||U / l||||12.0||||20190607134042|",
        "L||N",
    ])
    [run] = convert_astm_to_json(message)
    assert run['sample_id'] == '0000000001'
    assert [(r['code'], r['value']) for r in run['results']] == [('GOT', '125.0')]


def test_humastar_600_standard_astm():
    # HumaStar 600 manual 5.8.1: result in R-4, ^^^code, sample in O-3
    message = "\r".join([
        "H|\\^&|||HS600^1.0|||||||P|1394-97|20030916120000",
        "P|1|86|||Maxwell Smart||19780523|M",
        "O|1|12345||^^^COL\\^^^GLU|||20010506",
        "R|1|^^^COL|182|mg/dl||N||F||||20030916120000|HS600",
        "R|2|^^^GLU||mg/dl||||X",
        "L|1|N",
    ])
    [run] = convert_astm_to_json(message)
    assert (run['sender'], run['sample_id'], run['patient_name']) == ('HS600', '12345', 'Maxwell Smart')
    # GLU was cancelled (status X, no value) and is left out
    assert run['results'] == [
        {'code': 'COL', 'value': '182', 'unit': 'mg/dl', 'reference_range': '', 'flag': 'N'}]


def maglumi_capture_messages():
    """Maglumi Results.txt is a byte log of real transmissions; reassemble them."""
    with open(os.path.join(DOCS, 'Maglumi Results.txt'), encoding='utf-8') as handle:
        chunks = [line.split(':', 1)[1].strip() for line in handle if line.startswith('Mach')]
    sent = "".join(chunk for chunk in chunks if chunk not in ('<ENQ>', '<STX>', '<ETX>', '<EOT>'))
    sent = sent.replace('<CR>', '\r').replace('<Space>', ' ')
    return ['H|\\^&' + message for message in sent.split('H|\\^&') if message]


def test_maglumi_800_capture():
    runs = [run for message in maglumi_capture_messages() for run in convert_astm_to_json(message)]
    assert [(r['sender'], r['sample_id'], [x['code'] for x in r['results']]) for r in runs] == [
        ('MAGLUMI_800', 'VHS55693', ['FSH']),
        ('MAGLUMI_800', 'VHS63938', ['TSH', 'FT4', 'CRP', 'FT3']),
        ('MAGLUMI_800', 'VHS63952', ['CRP']),
        ('MAGLUMI_800', 'VHS64025', ['TSH', 'FSH']),
        ('MAGLUMI_800', 'VHS64400', ['PSA']),
    ]
    assert runs[1]['results'][0] == {'code': 'TSH', 'value': '0.531', 'unit': 'uIU/mL',
                                     'reference_range': '0.3 to 4.5', 'flag': 'N'}
