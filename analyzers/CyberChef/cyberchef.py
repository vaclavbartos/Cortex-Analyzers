#!/usr/bin/env python3
# encoding: utf-8

import json
import requests
from cortexutils.analyzer import Analyzer

class CyberchefAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)
        self.observable = self.get_param('data', None, 'Data missing!')
        self.service = self.get_param('config.service', None, 'Service is missing')
        self.url = self.get_param('config.url', None, 'URL is missing')

    def summary(self, raw):
        taxonomies = []
        level = 'info'
        namespace = 'CyberChef'
      
        # Set predicate for input
        predicate = 'input_data'
        taxonomies.append(self.build_taxonomy(level, namespace, predicate, raw['input_data']))
 
        # Set predicate for output_data
        predicate = 'output_data'
        taxonomies.append(self.build_taxonomy(level, namespace, predicate, raw['output_data']))
 
        return {"taxonomies": taxonomies}
   
    def run(self):
        try:
            observable = str(self.observable)
            url = self.url
            if self.service == 'FromHex':
                data = {"input": observable, "recipe":{"op":"From Hex", "args": ["Auto"]}} 
            elif self.service == "FromBase64":
                data = { "input": observable, "recipe":[{"op":"From Base64","args":["A-Za-z0-9+/=",True]}]}
            elif self.service == "FromCharCode":
                # Recipe from https://github.com/mattnotmax/cyberchef-recipes#recipe-3---from-charcode
                data = { "input": observable, "recipe":[{"op":"Regular expression","args":["User defined","([0-9]{2,3}(,\\s|))+",True,True,False,False,False,False,"List matches"]},{"op":"From Charcode","args":["Comma",10]},{"op":"Regular expression","args":["User defined","([0-9]{2,3}(,\\s|))+",True,True,False,False,False,False,"List matches"]},{"op":"From Charcode","args":["Space",10]}]}
            headers = { 'Content-Type': 'application/json' }
            r = requests.post(url.strip('/') + '/bake', headers=headers, data=json.dumps(data))
            response_bytes = r.text
            clean_bytes = response_bytes.strip('[').strip(']').split(',')
            output_data = ""
            for i in clean_bytes:
                output_data = str(output_data + str(chr(int(i))))
            self.report({ 'input_data': observable, 'output_data': output_data })
        except:
            self.error("Could not convert provided data.")

if __name__ == '__main__':
    CyberchefAnalyzer().run()
    