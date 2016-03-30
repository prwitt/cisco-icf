#! /usr/bin/env python2.7
"""
Created on Tue Mar 28 16:50:17 2016

@author: Paulo Renato
e-mail: prenato@gmail.com
version: 0.1

"""
# Currently the script is written to support VM with single interface only
# Requires ICFD 3.x northbound APIs, or newer releases

import json
import requests
import time

#
# Variables to change according to the ICF environment
#
icf_page = 'http://localhost:10000/icfb/v1' #change localhost:10000 to your ICFD IP Address
icf_usr_cred = '{"username":"admin","password":"Welcome_123"}' #Inform ICFD credentials
icf_usr_vdc = 'AWSCloud' 	#Inform the VDC you want to use
icf_usr_catalog = 'system_AWSCloud_CentOS6.3minimal' #Inform the catalog item you want to consume
icf_usr_network = 'mgmt-net' #Inform the network you want to use
icf_usr_vm_name = 'vm17-hello-py' #Inform the VM name you want
icf_usr_psa = 'true' #Inform wheter you want to access PSA or not, accepted values = true or false

print (time.strftime("%Y-%m-%d %H:%M:%S")) + " -- Make sure you updated variables from lines 20-26"
print (time.strftime("%Y-%m-%d %H:%M:%S")) + " -- Comment lines 28-30 of the script"
exit()

##############################################################
# get_keys()
# This function gets the token and the cookie from ICFB
# inputs: credentials provided by user 
# returns: token and cookie values
def get_keys():
	
	headers = {
	    'Content-Type': 'application/json',
	}

	saida = requests.post(icf_page+'/token', headers=headers, data=icf_usr_cred)

	if (saida.status_code == requests.codes.ok):
		cabecalho = saida.headers
	global chave
	global bolacha

	chave = cabecalho['x_icfb_token']
	bolacha = cabecalho['Set-Cookie'].split(";")[0].split("=")[1]
	
#	print chave
#	print bolacha
	

##############################################################
# list_img()
# This function lists the images available on ICFD 
# inputs: token and cookie from get_chave() 
# returns: list of images on ICFD
def list_img():
	
	headers = {
	    'x_icfb_token': chave,
	}
	cookies = {
		'JSESSIONID': bolacha,		
	}

	imagens = requests.get(icf_page+'/images', headers=headers, cookies=cookies)
	
	imagens_saida = json.loads(imagens.text)
	
	for element in imagens_saida['value']:
		element0 = json.dumps(element['properties']['name']).split('"')[1]
		element1 = json.dumps(element['properties']['os_info']['os']).split('"')[1]
		element2 = json.dumps(element['properties']['os_info']['version']).split('"')[1]
		print (element0+ ": " + element1 +" "+ element2)

##############################################################
# list_vcd()
# This function lists the ICF VCD OID 
# inputs: token and cookie from get_keys() 
# returns: VCD OID
def list_vdc():
	
	headers = {
	    'x_icfb_token': chave,
	}
	cookies = {
		'JSESSIONID': bolacha,		
	}

	vdcs = requests.get(icf_page+'/vdcs', headers=headers, cookies=cookies)
	
	vdcs_saida = json.loads(vdcs.text)
		
	for element in vdcs_saida['value']:
		element0 = json.dumps(element['properties']['oid']).split('"')[1]
		element1 = json.dumps(element['properties']['name']).split('"')[1]
		if (element1 == icf_usr_vdc):
					#print "we found "+element1
					global icf_usr_vdc_oid
					icf_usr_vdc_oid = element0

##############################################################
# list_img()
# This function lists the ICFD catalog item OID
# inputs: token and cookie from get_keys() 
# returns: catalog items OID
def list_catalog():
	
	headers = {
	    'x_icfb_token': chave,
	}
	cookies = {
		'JSESSIONID': bolacha,		
	}

	catalog_items = requests.get(icf_page+'/catalog-items', headers=headers, cookies=cookies)
	
	catalog_items_saida = json.loads(catalog_items.text)

#	print json.dumps(catalog_items_saida)
		
	for element in catalog_items_saida['value']:
		element0 = json.dumps(element['properties']['oid']).split('"')[1]
		element1 = json.dumps(element['properties']['name']).split('"')[1]
#		print (element1+ ": " + element0)
		if (element1 == icf_usr_catalog):
					#print "we found "+element1
					global icf_usr_catalog_oid
					icf_usr_catalog_oid = element0
					break

##############################################################
# list_networks()
# This function lists the networks OID 
# inputs: token and cookie from get_chave() 
# returns: network OID
def list_networks():
	
	headers = {
	    'x_icfb_token': chave,
	}
	cookies = {
		'JSESSIONID': bolacha,		
	}

	networks = requests.get(icf_page+'/networks', headers=headers, cookies=cookies)
	
	networks_saida = json.loads(networks.text)
		
	for element in networks_saida['value']:
		element0 = json.dumps(element['properties']['oid']).split('"')[1]
		element1 = json.dumps(element['properties']['name']).split('"')[1]
		if (element1 == icf_usr_network):
			#print "we found "+element1
			global icf_usr_network_oid
			icf_usr_network_oid = element0
			break


##############################################################
# create_usr_vm()
# This function creates a VM in the cloud via ICFD 
# inputs: token and cookie from get_chave(), VDC OID, Catalog OID,
#			PSA info, Network OID and VM Name 
# returns: status of the execution
def create_usr_vm():
	
	headers = {
			'x_icfb_token': chave
	}

	payload = {
			'name': icf_usr_vm_name,
			'vdc_oid': icf_usr_vdc_oid,
			'catalog_oid': icf_usr_catalog_oid,
			'enable_provider_services_access': icf_usr_psa,
			'nic_configurations' : [
				{'nic_index': '1',
				'is_dhcp': 'false',
				'network_oid': icf_usr_network_oid}
			]
		}
	
	cookies = {
		'JSESSIONID': bolacha,		
	}

	saida = requests.post(icf_page+'/instances', headers=headers, json=payload, cookies=cookies)

	if (saida.status_code == 202):
		cvm_instance = json.loads(saida.text)
		cvm_oid = cvm_instance['success']['links']['new_resource'].split("instances/")[1]
		cvm_status = requests.get(icf_page+'/instances/'+cvm_oid, headers=headers, cookies=cookies)
		cvm_status2 = json.loads(cvm_status.text)
		
#		print cvm_status.text
		
		for i in cvm_status2['value']:
			cvm_status3 = i['properties']['status']
#			print cvm_status3
		
		while ( cvm_status3 == "Create_In_Progress"):
			print (time.strftime("%Y-%m-%d %H:%M:%S")) + " - " + cvm_status3
			time.sleep(30)
			cvm_status = requests.get(icf_page+'/instances/'+cvm_oid, headers=headers, cookies=cookies)
			cvm_status2 = json.loads(cvm_status.text)
			#print cvm_status2
			for i in cvm_status2['value']:
				cvm_status3 = i['properties']['status']
			
		print "Cloud Virtual Machine -- " + icf_usr_vm_name + " -- Created with " + cvm_status3
		
	else:
		print "Execution Failed with error: " + str(saida.status_code)
		exit(saida.status_code)

get_keys()	
#list_img()
list_vdc()
list_catalog()
list_networks()
create_usr_vm()
