#! /usr/bin/env python

import urllib, sys
from xml.etree import ElementTree
from xml.etree import ElementPath
import os
import time
import urllib2
import hashlib
import errno
import shutil
import argparse

CWD = os.path.dirname( os.path.realpath( __file__ ) )
AWD = CWD + os.sep + "artifacts"

class DownloadArtifact(object):
    def __init__(self,url,group,artifact,version,repo="SNAPSHOTS",targetdir="."):
        self.url = url
        self.group = group
        self.artifact = artifact
        self.version = version
        self.repository = repo
        self.targetdir = targetdir
        print(self.artifact)

    def get_artifact_url(self):
        target_url = self.url + \
                "g=" + \
                self.group + \
                "&amp;a=" + \
                self.artifact + \
                "&amp;v=" + \
                self.version
                
        return target_url
    
    def download(self,url,file_name=None):
        def get_file_name(url,openUrl):
            if 'Content-Disposition' in openUrl.info():
                # if the response has Content-Disposition, try to get the filename from it
                cd = dict(map(
                              lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                              openUrl.info()['Content-Disposition'].split(';')))
                if 'filename' in cd:
                    filename = cd['filename'].strip("\"'")
                    if filename: return fileName
                    
            return os.path.basename(urlparse.urlsplit(openUrl.url)[2])
        
        try:
            r = urllib2.urlopen(urllib2.Request(url))
            fileName = file_name or get_file_name(url,r)
            self.checkpath(AWD)
            fullpath = AWD+os.sep+file_name
            with open(fullpath, 'wb') as f:
                shutil.copyfileobj(r,f)
        
        except urllib2.HTTPError as e:
            fullpath="Error Not Found "+ str(e.code)
            
        return fullpath
    
    def checkpath(self,path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def hashfile(self,sourceFile):
        GETCHUNK = 65536
        hasher_md5 = hashlib.md5()
        hasher_sha1 = hashlib.sha1()
        
        with open(sourceFile,'rb') as file_to_hash:
            buf = file_to_hash.read(GETCHUNK)
            while len(buf)>0:
                hasher_md5.update(buf)
                hasher_sha1.update(buf)
                buf = file_to_hash.read(GETCHUNK)
                
        return (hasher_sha1.hexdigest(),hasher_md5.hexdigest())
    
    def downloadArtifact(self):
        url = self.get_artifact_url()
        data = urllib2.urlopen(url).read()
        doc = ElementTree.XML(data)
        elements = ElementPath.findall(doc, ".//artifact")
        artifacts = []
        
        #create a list of artifacts
        for x in elements:
            artifacts.append((x.find("resourceURI").text,
                              x.find("groupId").text, 
                              x.find("artifactId").text, 
                              x.find("version").text, 
                              x.find("packaging").text,
                              x.find("extension").text,
                              x.find("repoId").text, 
                              x.find("contextId").text, 
                              x.find("pomLink").text, 
                              x.find("artifactLink").text))
            

        #Filter on snapshots or releases
        artifacts = [artifact for artifact in artifacts if artifact[6].lower() == self.repository.lower()]
        #Filter on group
        artifacts = [artifact for artifact in artifacts if artifact[1].lower() == self.group.lower()]
        #Filter on artifact name
        artifacts = [artifact for artifact in artifacts if artifact[2].lower() == self.artifact.lower()]
        #print artifacts
        artifact_name=""
        if artifacts:
            #Get the last artifact in the list
            artifact = artifacts[-1]
            
            artifact_url = artifact[9]
            artifact_name = artifact[0].split('/')[-1]
            dlfile = self.download(artifact_url, artifact_name)
            if "Error Not Found 404" in dlfile:
                print("Downloading from: "+artifact[0])
                #Try the download again using the undirected link
                dlfile = self.download(artifact[0], artifact_name)

            print("Downloaded: "+dlfile)
            file_hashes = self.hashfile(dlfile)
            print("SHA1: "+file_hashes[0])
            print("MD5 : "+file_hashes[1])
            
                    
        print("-"*40)

        return artifact_name 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nxurl', required=True)
    parser.add_argument('--group', required=True)
    parser.add_argument('--artifact', required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--repo', required=True)
    args = parser.parse_args()

    d = DownloadArtifact(args.nxurl, args.group, args.artifact, args.version, args.repo)
    d.downloadArtifact()

if __name__ == "__main__":
    main()

