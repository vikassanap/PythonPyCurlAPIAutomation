import pycurl
import cStringIO
import urllib
from manage_extracts import *
from write_xml import *
from assert_body import *
from extract_body import *
from match_response_body import *
import os
PATH = os.getcwd()
DIR = os.path.dirname(os.path.realpath(__file__))
import logging

def post_request(project_name,test_case_response_extract_body,test_case_response_assert_body,testcase_name, testcase_id, api, suite, group,request_url,request_headers,request_body_type, request_parameters,response_code,response_header_list,response_body,test_case_response_body_type,test_case_response_body_match,test_case_response_extract_headers,primary_request,follow_redirects_flag,enable_cookie_flag):
    extraction_details = ''
    reason_of_failure = ''
    test_output = []
    headers = {}
    request_body = None
    reason = ''
    file_flag = 'false'
    def header_function(header_line):
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line:
            return
        name, value = str(header_line).split(':', 1)
        name = name.strip()
        #print name
        value = value.strip()
        name = name.lower()
        headers[str(name)] = str(value)

    buf = cStringIO.StringIO()
    header = cStringIO.StringIO()
    conn = pycurl.Curl()
    conn.setopt(conn.URL, str(request_url))
    if(request_headers != []):
        conn.setopt(conn.HTTPHEADER, request_headers)
    if(request_body_type == 'form'):
        temp_list = []
        for parameter in request_parameters:
            if str(parameter['@type']) == 'text':
                temp_list.append((str(parameter['@name']),str(parameter['@value'])))
            elif str(parameter['@type']) == 'file':
                temp_list.append((str(parameter['@name']), (conn.FORM_FILE, PATH+"/test_data/upload/"+str(parameter['@value']))))
                file_flag = 'true'
        if file_flag == 'true':
            pairs = temp_list
            conn.setopt(conn.HTTPPOST, pairs)
        else:
            pairs = urllib.urlencode(temp_list)
            conn.setopt(conn.POSTFIELDS, pairs)
        request_body = str(request_parameters)
    else:
        conn.setopt(conn.POSTFIELDS, str(request_parameters))
        request_body = str(request_parameters)
    conn.setopt(conn.WRITEFUNCTION, buf.write)
    conn.setopt(conn.HEADERFUNCTION, header_function)
    if(enable_cookie_flag == 'true'):
        conn.setopt(pycurl.COOKIEJAR, PATH+'/test_data/temp/cookie.txt')
        conn.setopt(pycurl.COOKIEFILE, PATH+'/test_data/temp/cookie.txt')
    if(follow_redirects_flag == 'true'):
        conn.setopt(conn.FOLLOWLOCATION, True)
    conn.setopt(conn.VERBOSE , 1)
    conn.perform()
    response_body_result = 'NA'
    if test_case_response_body_type == 'file':
        #print "Inside file,nothing"
        expected_file_name = response_body
        #print PATH+"/../test_data/download/"+expected_file_name
        fp = open(PATH+"/test_data/download/"+expected_file_name, "wb")
        fp.write(buf.getvalue())
        data = ''
    else:
        data = str(buf.getvalue())
    #print str(header.getvalue())
    #data = str(buf.getvalue())
    code = conn.getinfo(pycurl.HTTP_CODE)
    if test_case_response_body_type == 'file':
        #print "Response Body Matching is not available for file download. Please check downloaded at location", PATH+"/../test_data/download/"+expected_file_name
        response_body_result = 'pass'
    else:
        (response_body_result,reason_of_failure) = match_response_body(test_case_response_body_type, test_case_response_body_match, data, response_body)

    if(code == int(response_code)):
        response_body_code = 'pass'
    else:
        response_body_code = 'fail'
        reason_of_failure = reason_of_failure + ", Response Code Match Error: Expected Response Code => "+str(response_code)+" Actual Response Code => "+ str(code)
    buf.close()
    header.close()
    response_header_result = 'NA'
    sep = ';'
    for header in response_header_list:
        temp = header.split(':',1)
        name = temp[0]
        value = temp[1]
        try:
            if(headers[name.lower()] != value.lower()):
                #print "Invalid value for header: ",name,value
                response_header_result = 'fail'
                reason_of_failure = reason_of_failure+", Response Header Match Error : Expected Header with Value => "+name+"="+value
                break
            else:
                response_header_result = 'pass'
        except KeyError:
            #print "Response header is not found ", header
            response_header_result = 'fail'
            reason_of_failure = reason_of_failure + ", Response Header Match Error : Header is not found =>"+name+"="+value 
            break
    try:
        for header in test_case_response_extract_headers:
            if str(str(header['@name']).split(':',1)[0]) == 'REGEX':
                temp_container = extract_header(str(header['@name']).split(':',1)[1],headers)
            else:
                temp_container = headers[str(header['@name'])].split(sep, 1)[0]
            store_header(str(header['#text']),temp_container)
            extraction_details = extraction_details + " Extracted Header "+ str(header['#text']) +" with value "+temp_container +"\n"
    except KeyError:
        extraction_details = extraction_details + "Key error while header value extraction"
        logging.error("Key error while header extraction")
    assert_body_result = 'NA'
    (assert_body_result,reason) = assert_body(data,test_case_response_assert_body)
    reason_of_failure = reason_of_failure + reason
    extract_body_result = extract_body(data,test_case_response_extract_body)
    """
    try:
        logging.info("delete_request:Inside Delete Request")
        logging.info("delete_request:request_url: ",request_url)
        logging.info("delete_request:request_headers: ",request_headers)
        logging.info("delete_request:response_code: ",response_code)
        logging.info("delete_request:response_header_list: ",response_header_list)
        logging.info("delete_request:response_body: ",response_body)
        logging.info("delete_request:------Response------")
        logging.info("delete_request:actual response_body: ",data)
        logging.info("delete_request:actual response_code: ",code)
        logging.info("delete_request:actual response_headers: ",headers)
        logging.info("delete_request:------Result-------")
        logging.info("delete_request:response_code_match_result: ",response_body_code)
        logging.info("delete_request:response_body_result: ",response_body_result)
        logging.info("delete_request:response_header_result: ",response_header_result)
        logging.info("delete_request:assert_body_result: ",assert_body_result) 
        logging.info("delete_request:extract_body_result: ",extract_body_result)
        logging.info("delete_request:reason_of_failure: ",reason_of_failure)
        logging.info("delete_request:extract_header_result: ",extraction_details)
    except TypeError:
            pass
    """
    overall_result = 'fail'
    if((response_body_result == 'pass' or response_body_result == 'NA') and (response_header_result == 'pass' or response_header_result == 'NA') and response_body_code == 'pass' and (assert_body_result == 'pass' or assert_body_result == 'NA')):
        overall_result = 'pass'
    #logging.info("post_request:overall_result: ",overall_result)
    write_result(project_name,testcase_name, testcase_id, api, suite, group, "post", request_url, request_headers, request_body, response_code, response_header_list, response_body, code, headers, data, response_header_result, response_body_result, response_body_code, overall_result,primary_request,assert_body_result,reason_of_failure,extraction_details,extract_body_result)



