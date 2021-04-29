import re
import hashlib

from pysourcecodesec import logger

'''
The following test modules are the default available tests for Bandit
    B101	assert_used
    B102	exec_used
    B103	set_bad_file_permissions
    B104	hardcoded_bind_all_interfaces
    B105	hardcoded_password_string
    B106	hardcoded_password_funcarg
    B107	hardcoded_password_default
    B108	hardcoded_tmp_directory
    B110	try_except_pass
    B112	try_except_continue
    B201	flask_debug_true
    B301	pickle
    B302	marshal
    B303	md5
    B304	ciphers
    B305	cipher_modes
    B306	mktemp_q
    B307	eval
    B308	mark_safe
    B309	httpsconnection
    B310	urllib_urlopen
    B311	random
    B312	telnetlib
    B313	xml_bad_cElementTree
    B314	xml_bad_ElementTree
    B315	xml_bad_expatreader
    B316	xml_bad_expatbuilder
    B317	xml_bad_sax
    B318	xml_bad_minidom
    B319	xml_bad_pulldom
    B320	xml_bad_etree
    B321	ftplib
    B323	unverified_context
    B324	hashlib_new_insecure_functions
    B325	tempnam
    B401	import_telnetlib
    B402	import_ftplib
    B403	import_pickle
    B404	import_subprocess
    B405	import_xml_etree
    B406	import_xml_sax
    B407	import_xml_expat
    B408	import_xml_minidom
    B409	import_xml_pulldom
    B410	import_lxml
    B411	import_xmlrpclib
    B412	import_httpoxy
    B413	import_pycrypto
    B501	request_with_no_cert_validation
    B502	ssl_with_bad_version
    B503	ssl_with_bad_defaults
    B504	ssl_with_no_version
    B505	weak_cryptographic_key
    B506	yaml_load
    B507	ssh_no_host_key_verification
    B601	paramiko_calls
    B602	subprocess_popen_with_shell_equals_true
    B603	subprocess_without_shell_equals_true
    B604	any_other_function_with_shell_equals_true
    B605	start_process_with_a_shell
    B606	start_process_with_no_shell
    B607	start_process_with_partial_path
    B608	hardcoded_sql_expressions
    B609	linux_commands_wildcard_injection
    B610	django_extra_used
    B611	django_rawsql_used
    B701	jinja2_autoescape_false
    B702	use_of_mako_templates
    B703	django_mark_safe
'''

bandit_cmd = 'python3 -m bandit -t B102,B104,B105,B106,B107,B108,B307,B404,B506,B602,B603,B604,B605,B606,B607,B609 \
--format custom --msg-template "{relpath}:{line}:{test_id}:{confidence}:{severity}:{msg}"'

csv_header = "num_of_strings,cred_vars_present,wordcount,open_present,popen_present,system_present,exec_present,"
csv_header += "eval_present,input_present,hardcoded_address_present,parses_yaml,is_conditional,num_of_invocations,vulnerability"
num_of_classes = 4
num_of_features = 13
labels = {
    "none":"none",
    "B102":"calling_external_function",
    "B104":"hardcoded_information",
    "B105":"hardcoded_information",
    "B106":"hardcoded_information",
    "B107":"hardcoded_information",
    "B108":"hardcoded_information",
    "B307":"calling_external_function",
    "B404":"calling_external_function",
    "B506":"loading_yaml",
    "B602":"calling_external_function",
    "B603":"calling_external_function",
    "B604":"calling_external_function",
    "B605":"calling_external_function",
    "B606":"calling_external_function",
    "B607":"calling_external_function",
    "B609":"calling_external_function",
}
classes = [
    "none",
    "calling_external_function",
    "hardcoded_information",
    "loading_yaml"
]   

def num_of_strings(line):
    singles = 0
    doubles = 0
    for i in line:
        if i == '"':
            doubles += 1
        if i == "'":
            singles += 1
    if singles % 2 == 1:
        singles -= 1
    if doubles % 2 == 1:
        doubles -= 1
    return int(singles / 2 + doubles / 2)

def cred_vars_present(line):
    keywords = {
        "pass",
        "p@ass",
        "pwd",
        "login",
        "user",
        "acct",
        "account",
        "email",
        "e-mail",
        "name",
        "credentials"
    }
    for keyword in keywords:
        if len(keyword) > len(line):
            continue
        for i in range(0, len(line) - len(keyword) + 1):
            if line[i:i+len(keyword)].lower() == keyword:
                return 1
    return 0

def wordcount(line):
    return len(line.split())

def open_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "open(":
            return 1
    return 0

def popen_present(line):
    if len(line) < 7:
        return 0
    for i in range(0, len(line) - 5):
        if line[i:i+6] == "popen(":
            return 1
    return 0

def system_present(line):
    if len(line) < 8:
        return 0
    for i in range(0, len(line) - 6):
        if line[i:i+7] == "system(":
            return 1
    return 0

def exec_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "exec(":
            return 1
    return 0

def eval_present(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "eval(":
            return 1
    return 0

def input_present(line):
    if len(line) < 7:
        return 0
    for i in range(0, len(line) - 5):
        if line[i:i+6] == "input(":
            return 1
    return 0

def hardcoded_address_present(line):
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
    if len(ip) > 0:
        return 1
    return 0

def parses_yaml(line):
    if len(line) < 6:
        return 0
    for i in range(0, len(line) - 4):
        if line[i:i+5] == "load(" or line[i:i+4] == "yaml" or line[i+1:i+5] == "yaml":
            return 1
    return 0

def is_conditional(line):
    line = line.strip()
    if line[0:2] == "if" or line[0:5] == "while" or line[0:4] == "elif" or line[0:3] == "else":
        return 1
    return 0

def num_of_invocations(line):
    inv = 0
    for i in range(len(line)):
        if line[i] == '(':
            if i == 0:
                continue
            if line[i-1] != ' ' and line[i-1] != '=':
                inv += 1
    return inv

features = {
    0:num_of_strings,
    1:cred_vars_present,
    2:wordcount,
    3:open_present,
    4:popen_present,
    5:system_present,
    6:exec_present,
    7:eval_present,
    8:input_present,
    9:hardcoded_address_present,
    10:parses_yaml,
    11:is_conditional,
    12:num_of_invocations
}

