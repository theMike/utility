#!/usr/bin/python
# ad-phonelist.py
"""
  This script is used to create a phone number list page
  on Confluence. The script takes confluence page number,
  page id, and page space at the commandline and will list
  all users with a phone#
  This script is intended to be executed regularly.
"""


import sys
import ldap
import ldif
import ldap.modlist
import xmlrpclib
import argparse
from obfussee import illumit


CONFLUENCE_URL = "https://jira.corp.com/confluence/rpc/xmlrpc"
from html import HTML

SERVER="ldap://corp.local"
DN="cn=Domain-DNS,cn=Schema,cn=Configuration,dn=corp,dn=local"

BASE_CORPSOFT="OU=corp,DC=corp,DC=local"
BASE_CORPGLOBAL="OU=Corp,DC=corp,DC=local"
CRITERIA="(&(objectClass=user)(userAccountControl=512))"
ATTRIBUTES = ['displayName','company']

def confluence_connect():
    client = xmlrpclib.Server(CONFLUENCE_URL, verbose= 0 ) 
    auth_token = client.confluence2.login(CONFLUENCE_LOGIN, CONFLUENCE_PASSWORD)
    page = client.confluence2.getPage(auth_token, PAGE_ID)
    return page
    
class ConfluenceConnect(object):
    def __init__(self):
        self.auth_token=None
        self.page=None
        self.sub_page=None
        self.pageid=None
        self.client=None
        
    def connect(self,confluenceurl,username,password):
        self.client = xmlrpclib.Server(confluenceurl, verbose= 0 ) 
        self.auth_token = self.client.confluence2.login(username, password)
        
    def getpage_main(self,pageid):
        self.page = self.client.confluence2.getPage(self.auth_token,pageid)
        
    def getpage(self,confluence_space, confluence_title):
        self.page=self.client.confluence2.getPage(self.auth_token,confluence_space, confluence_title)
        
    def getspace(self,spaceName):
        space = self.client.confluence2.getSpace(self.auth_token,spaceName)
                
    def showpage_sub(self):
        print(self.page)
        
    def logout(self):
        self.client.confluence2.logout(self.auth_token)
        
    def setpage_content_text(self,status_text):
        c =ConfluenceUpdate(self.page, self.client, self.auth_token)
        c.set_content_text(status_text)
        c.write_content()
        
    def __del__(self):
        self.logout()
         
class ConfluenceUpdate(object):
    def __init__(self,page,client,token):
        self.cpage=page
        self.cclient=client
        self.ctoken=token
        
    def set_content_text(self,status_text):
        self.cpage['content'] = status_text
        
    def write_content(self):
        self.cclient.confluence2.storePage(self.ctoken,self.cpage)
        
def configure_options():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--user','-u',required=True,help='Confluence user login')
    parser.add_argument('--password','-p', required=True, help='Confluence password')
    parser.add_argument('--domain','-d',  help='User domain')
    parser.add_argument('--pageid','-i', help="Confluence page id")
    parser.add_argument('--pagespace','-s', help="Confluence page space")
    parser.add_argument('--pagename','-n', help="Confluence sub-page title")
    parser.add_argument('--outfile','-o', help="Output to file only")
    return parser

class report(object):
  
  def __init__(self):
    self.h=HTML('html')
    self.h.p("This list will automatically update")
    self.h.style('table {border, td, th: 1px solid black; border-collapse: collapse;} \
        th, td { padding: 5px; text-align: left;}')
    self.h.h2("CorpSoft Employee Phone list")
    self.t=None
    self.r=None
    
  def header(self):
    self.t=self.h.table(boarder='1')
    self.r=self.t.tr
    self.r.th('Employee')
    self.r.th('Telephone#') 
    self.r.th('Mobile#')
    
  def add_item(self,line):
    r=self.t.tr
    r.td(line[0])
    r.td(line[1])
    r.td(line[2])
    
  def get_table(self):
    return str(self.h)

def get_ad_users(ad_server,base_dn,auth_user,auth_password):
    l=None
    try:
        l=ldap.initialize(ad_server)
        l.protocol_version = ldap.VERSION3
        l.set_option(ldap.OPT_REFERRALS,0)
        l.simple_bind_s(auth_user,auth_password)
    except l.INVALID_CREDENTIALS:
        l.unbind()
        return "wrong username or password"
    except l.SERVER_DOWN:
        return "AD server is not available"

    result = l.search_s(base_dn,ldap.SCOPE_SUBTREE,"(cn=*)")
    results = [entry for dn, entry in result if isinstance(entry, dict)]

    return results

def main():
    rep = report()
    rep.header()
    p = configure_options()
    args = p.parse_args()
    list_corpsoft = get_ad_users(SERVER,BASE_CORPSOFT,args.user+"@"+args.domain,illumit(args.password))
    list_corpglobal = get_ad_users(SERVER,BASE_CORPGLOBAL,args.user+"@"+args.domain,illumit(args.password))
    
    ad_corp = list_corpsoft + list_corpglobal

    for items in ad_corp:
        k=[]
        #Only display users with a phone# set in AD
        show_user=True
        if 'userAccountControl' in items:
            if items['userAccountControl'][0] == '514':
                show_user=False
                
        if 'name' in items:
            k.append(items['name'][0])

        if 'telephoneNumber' in items:
            k.append(items['telephoneNumber'][0])

            if 'mobile' in items:
                k.append(items['mobile'][0])
            else:
                k.append("")

        else:
            show_user=False
            k.append("")
            k.append("")

        if show_user:
           rep.add_item(k)
        
    phone_table= rep.get_table()

    if args.outfile is None:
        confluence = ConfluenceConnect()
        confluence.connect(CONFLUENCE_URL, args.user, illumit(args.password))
        confluence.getpage_main(args.pageid)
        confluence.getpage(args.pagespace, args.pagename)    
        confluence.setpage_content_text(phone_table)
    else:
        print("write to file: "+args.outfile)
        if len(args.outfile) > 0:
            with open(args.outfile,'w+') as userphone:
                userphone.write(phone_table)


    
if __name__ == "__main__":
  main()


