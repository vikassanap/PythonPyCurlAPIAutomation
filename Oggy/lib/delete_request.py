import pycurl
import cStringIO
from manage_extracts import *
from write_xml import *
from assert_body import *
from extract_body import *
from match_response_body import *
import urllib
import os
PATH = os.getcwd()
import logging
DIR = os.path.dirname(os.path.realpath(__file__))

def delete_request(project_name,test_case_response_extract_headers,test_case_response_extract_body,test_case_response_assert_body,testcase_name, testcase_id, api, suite,group,request_url,request_headers,response_code,response_header_list,response_body,test_case_response_body_type,test_case_response_body_match,primary_request,follow_redirects_flag,enable_cookie_flag,request_body_type, request_body_value_dp):
    extraction_details = ''
    test_output = []
    reason = ''
    reason_of_failure = ''
    headers = {}
    def header_function(header_line):
        header_line = header_line.decode('iso-8859-1')
        if ':' not in header_line:
            return
        name, value = header_line.split(':', 1)
        name = name.strip()
        value = value.strip()
        name = name.lower()
        headers[str(name)] = str(value)

    buf = cStringIO.StringIO()
    header = cStringIO.StringIO()
    conn = pycurl.Curl()
    temp_list = []
    if request_body_value_dp != '{}':
        try:
            for parameter in request_body_value_dp:
                if str(parameter['@type']) == 'text':
                    temp_list.append((str(parameter['@name']),str(parameter['@value'])))
            conn.setopt(conn.URL, str(request_url)+'?'+ urllib.urlencode(temp_list))
            temp_url = str(request_url)+'?'+ urllib.urlencode(temp_list)
        except KeyError:
            pass
    else:
        conn.setopt(conn.URL, str(request_url))
        temp_url = str(request_url)
    conn.setopt(conn.CUSTOMREQUEST, "DELETE")
    conn.setopt(conn.HTTPHEADER, request_headers)
    conn.setopt(conn.WRITEFUNCTION, buf.write)
    conn.setopt(conn.HEADERFUNCTION, header_function)
    conn.setopt(conn.VERBOSE , 1)
    if(enable_cookie_flag == 'true'):
        conn.setopt(pycurl.COOKIEFILE, PATH+'/test_data/temp/cookie.txt')
    if(follow_redirects_flag == 'true'):
        conn.setopt(conn.FOLLOWLOCATION, True)
    conn.setopt(conn.VERBOSE , 1)
    conn.perform()
    if test_case_response_body_type == 'file':
        expected_file_name = response_body
        fp = open(PATH+"/test_data/download/"+expected_file_name, "wb")
        fp.write(buf.getvalue())
        data = ''
    else:
        data = str(buf.getvalue())
    code = conn.getinfo(pycurl.HTTP_CODE)
    response_body_result = 'NA'

    if test_case_response_body_type == 'file':
        response_body_result = 'pass'
    else:
        (response_body_result,reason_of_failure) = match_response_body(test_case_response_body_type, test_case_response_body_match, data, response_body)

    if(code == int(response_code)):
            response_body_code = 'pass'
    else:
            response_body_code = 'fail'
            reason_of_failure = reason_of_failure + ", Response Code Match Error: Expected Response Code => "+str(response_code)+" Actual Response Code => "+ str(code)
    buf.close()
    if test_case_response_body_type == 'file':
        fp.close()
    header.close()
    conn.close()

    response_header_result = 'NA'
    sep = ';'
    for header in response_header_list:
        temp = header.split(':',1)
        name = temp[0]
        value = temp[1]
        try:
            if(headers[name.lower()] != value.lower()):
                response_header_result = 'fail'
                reason_of_failure = reason_of_failure+", Response Header Match Error : Expected Header with Value => "+name+"="+value
                break
            else:
                response_header_result = 'pass'
        except KeyError:
            response_header_result = 'fail'
            reason_of_failure = reason_of_failure+", Response Header Match Error : Expected Header with Value => "+name+"="+value
            break
    try:
        for header in test_case_response_extract_headers:
            if str(str(header['@name']).split(':',1)[0]) == 'REGEX':
                temp_container = extract_header(str(header['@name']).split(':',1)[1],headers)
            else:
                temp_container = headers[str(header['@name'])].split(sep, 1)[0]
            store_header(str(header['#text']),temp_container)
            extraction_details = extraction_details + " Extracted Header "+ str(header['#text']) +" with value "+temp_container+"\n"
    except KeyError:
        extraction_details = extraction_details + "Key error while header value extraction"
        logging.error("Key error while header extraction")
        pass
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
    write_result(project_name,testcase_name, testcase_id, api, suite, group, "delete", temp_url, request_headers, "", response_code, response_header_list, response_body, code, headers, data, response_header_result, response_body_result, response_body_code, overall_result,primary_request,assert_body_result,reason_of_failure,extraction_details,extract_body_result)



