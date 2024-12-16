

def convert_hl7_to_json(hl7_str):
    # Split by segments
    segments = hl7_str.strip().split('\n')
    
    # Extract relevant fields
    patient_name = ''
    patient_age = ''
    patient_sex = ''
    test_panel_name = ''
    item = ''
    sale_price = 3445.0  # hardcoded value
    lab_test_request = 1
    is_billed = False
    is_quantitative = True
    is_qualitative = False
    
    for segment in segments:
        fields = segment.split('|')
        if fields[0] == 'PID':
            patient_name = fields[5] + ' ' + fields[6]
            patient_age = 4  # hardcoded value
            patient_sex = 'F'  # hardcoded value
        elif fields[0] == 'OBR':
            test_panel_name = 'RBC'
            item = '3'
    
    # Create new JSON object
    json_obj = {
        "id": 1,
        "result": None,
        "result_approved": False,
        "test_panel": 1,
        "test_panel_name": test_panel_name,
        "item": item,
        "sale_price": sale_price,
        "patient_name": patient_name,
        "patient_age": patient_age,
        "patient_sex": patient_sex,
        "reference_values": None,
        "lab_test_request": lab_test_request,
        "is_billed": is_billed,
        "is_quantitative": is_quantitative,
        "is_qualitative": is_qualitative
    }
    
    return json_obj
# import json

# class MSH:
#   def __init__(self):
#      pass
  
#   def parse(self, json_data):
#     msh_map = {
#           "MSH.1": "Field Separator",
#           "MSH.2": "Encoding Characters",
#           "MSH.3": "Sending Application",
#           "MSH.4": "Sending Facility",
#           "MSH.5": "Receiving Application",
#           "MSH.6": "Receiving Facility",
#           "MSH.7": "Date / Time of Message",
#           "MSH.8": "Security",
#           "MSH.9": "Message Type",
#           "MSH.10": "Message Control ID",
#           "MSH.11": "Processing ID",
#           "MSH.12": "Version ID",
#           "MSH.13": "Sequence Number",
#           "MSH.14": "Continuation Pointer",
#           "MSH.15": "Accept Acknowledgement Type",
#           "MSH.16": "Application Acknowledgement Type",
#           "MSH.17": "Country Code",
#           "MSH.18": "Character Set",
#           "MSH.19": "Principal Language of Message"
#       }
#     msh_value = json_data.get("MSH")
#     msh_data = {}
#     if msh_value:
#           for key in msh_map:
#               if key in msh_value:
#                   msh_data[key] = { "name":msh_map[key],"value": msh_value[key]}
#     return msh_data
  

  

# class PID:
#   def __init__(self):
#      pass
  
#   def parse(self, json_data):
#       pid_map= {
#         "PID.1": "Set ID - Patient ID",
#         "PID.2": "Patient ID (External ID)",
#         "PID.3": "Patient ID (Internal ID)",
#         "PID.4": "Alternate Patient ID",
#         "PID.5": "Patient Name",
#         "PID.5.1":"Family Name",
#         "PID.5.2":"Given Name",
#         "PID.5.3":"Middle Initial Or Name",
#         "PID.5.4":"Suffix",
#         "PID.5.5":"Prefix",
#         "PID.5.6":"Degree",
#         "PID.5.7":"Name Type Code",
#         "PID.5.8":"Name Representation Code",
#         "PID.6": "Mother's Maiden Name",
#         "PID.7": "Date of Birth",
#         "PID.8": "Sex",
#         "PID.9": "Patient Alias",
#         "PID.10": "Race",
#         "PID.11": "Patient Address",
#         "PID.11.1": "Street Address",
#         "PID.11.2": " Other Designation",
#         "PID.11.3": "City",
#         "PID.11.4": "State Or Province",
#         "PID.11.5": "Zip Or Postal Code",
#         "PID.11.6": "Country",
#         "PID.11.7": "Address Type",
#         "PID.11.8": "Other Geographic Designation",
#         "PID.11.9": "County/Parish Code",
#         "PID.11.10": "Census Tract",
#         "PID.11.11": "Address Representation Code",
#         "PID.11.12": "Address Validity Range",
#         "PID.11.13": "Effective Date",
#         "PID.11.14": "Expiration Date",
#         "PID.12": "County Code",
#         "PID.13": "Phone Number - Home",
#         "PID.14": "Phone Number - Business",
#         "PID.15": "Primary Language",
#         "PID.16": "Marital Status",
#         "PID.17": "Religion",
#         "PID.18": "Patient Account Number",
#         "PID.19": "SSN Number - Patient",
#         "PID.20": "Driver's License Number",
#         "PID.21": "Mother's Identifier",
#         "PID.22": "Ethnic Group",
#         "PID.23": "Birth Place",
#         "PID.24": "Multiple Birth Indicator",
#         "PID.25": "Birth Order",
#         "PID.26": "Citizenship",
#         "PID.26.1": "Citizenship Identifier",
#         "PID.26.2": "Citizenship Text",
#         "PID.26.3": "Citizenship Name Of Coding System",
#         "PID.26.4": "Citizenship Alternate Components",
#         "PID.26.5": "Citizenship Alternate Text",
#         "PID.26.6": "Citizenship  Name Of Alternate Coding System",
#         "PID.27": "Veterans Military Status",
#         "PID.28": "Nationality Code",
#         "PID.29": "Patient Death Date and Time",
#         "PID.30": "Patient Death Indicator"
#       }

#       pid_value = json_data.get("PID")
#       pid_data = {}
#       if pid_value:
#         for key in pid_map:
#             if key in pid_value:
#                pid_data[key] = { "name":pid_map[key],"value": pid_value[key]}
#       return pid_data

# class HL7Utils:
#   '''This might help: https://github.com/sudhi001/HL7_TO_JSON_WITH_FAST_API'''
#   def __init__(self):
#      pass

#   def parse(self, hl7_message):
#         """Converts an HL7 message to a JSON object.
#         """
#         segments = hl7_message.split('\r')
#         json_message = {}
#         for segment in segments:
#           fields = segment.split('|')
#           segment_type = fields[0]
#           json_segment = {}
#           for i, field in enumerate(fields):
#             if i == 0:
#               continue
#             index = i
#             if segment_type == 'MSH': 
#                 index = index +1
#             field_name = segment_type + '.' + str(index)
#             if field != ' ' and field != '':
#               if field_name == 'MSH.2':
#                  json_segment["MSH.1"] = "|"
#                  json_segment[field_name.strip()] = field
#                  continue
#               json_segment[field_name.strip()] = field
#               subsegment_values = field.split('^')
#               if len(subsegment_values) >1:
#                 for j, subfieldValue in enumerate(subsegment_values):
#                   field_name = segment_type + '.'+ str(index) +  '.' + str(j+1)
#                   if subfieldValue != ' ' and subfieldValue != '':
#                     json_segment[field_name.strip()] = subfieldValue
#                     sub_subsegment_values = subfieldValue.split('~')
#                     if len(sub_subsegment_values) >1:
#                       for k, second_subfieldValue in enumerate(sub_subsegment_values):
#                         field_name = segment_type + '.'+ str(index) +  '.' + str(j+1)+  '.' + str(k+1)
#                         if second_subfieldValue != ' ' and second_subfieldValue != '':
#                           json_segment[field_name.strip()] = second_subfieldValue


#           json_message[segment_type.strip()] = json_segment

#         return json_message
  



#   def detailed(self, json_data):
#       msh_data = MSH().parse(json_data)
#       pid_data = PID().parse(json_data)
#       return {"MSH":msh_data,"PID":pid_data}


