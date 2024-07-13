# -*- coding: utf-8 -*-

import re
import ojson
import glob
from typing import Optional

class SrcReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.files = glob.glob(self.file_path)
        self.data_order = ["광대 뼈 수술","눈 아래 안륜근융비술 (애교수술)","눈 아래 주름제거술","눈 아래 지방 제거술","눈매 교정술","눈썹 올림술","눈트임 수술 (내안각, 외안각 성형술)","들창코 교정술","레이저 박피술","보툴리눔 독소 (Botox)","보형물을 이용한 유방 확대 수술","복부 성형술","실을 이용한 주름 개선술","쌍꺼풀 수술","악교정수술","안검하수 교정술","얼굴 올림술 (얼굴 주름 성형술)","위 눈꺼풀 주름 제거술","유두 성형술","유방 고정술 (유방 리프트, 유방하수 고정술)","유방 제거 후 유방 재건술, 유두 유륜 재건술","유방 축소술 (여성)","유방 축소술 (여성형 유방증수술)","이마 올림술","지방 흡인술 (지방 성형술)","지방이식, 지방주입","코 축소술 (매부리코 교정술, 휜코 교정술, 코볼 축소술)","코끝 성형술","콧등 융비술","턱끝뼈 수술","피부 필러","화학박피술", "레이저 제모"]
        self.data = {
            t: None for t in self.data_order
        }
        self.paragraph_order = ["title", "purpose", "information", "result", "caution", "notice", "cost"]
        self.rename_title = {
            "title": "수술명",
            "purpose": "수술을 하는 목적",
            "information":"수술의 진행과정",
            "result":"수술의 예상 결과",
            "caution":"수술의 부작용",
            "notice":"수술 전 고려사항",
            "cost":"수술의 가격"
        }
        for file in self.files:
            with open(file, "r") as f:
                fData = ojson.load(f)
                self.data[fData["title"]] = fData

    def get_document(self, title: Optional[str] = None, index: Optional[str] = None) -> str:
        if title:
            return self.data[title]
        
        elif index:
            if type(index) == str:
                if ' ' in index:
                    index = index.split(' ')[0]
                index = re.sub(r'\D', '', index)
                index = int(index)
            return self.data[self.data_order[index-1]]
        
    def get_paragraph(self, keyword_name: str, document: dict[str, str], index: Optional[str] = None, name: Optional[str] = None):
        paragraph = "# " + keyword_name + "\n"
        if index:
            if type(index) == str:
                try:
                    index = index.replace(",", " ")
                    index = re.sub(r'\D ', '', index)
                    index = list(map(int, index.split(" ")))
                except:
                    index = [1, 2, 3, 4, 5, 6]
            paragraph += "\n".join([f"## {self.rename_title[self.paragraph_order[i]]}\n" + document[self.paragraph_order[i]] for i in index])
            return paragraph
        
        elif name:
            return document[name]
        
    def get_keyword_name(self, index: str):
        if ' ' in index:
            index = index.split(' ')[0]
        index = re.sub(r'\D', '', index)
        index = int(index)
        return self.data_order[index-1]
    
    def get_community_keyword(self, index: str):
        if ' ' in index:
            index = index.split(' ')[0]
        index = re.sub(r'\D', '', index)
        index = int(index)
        return self.data[self.data_order[index-1]]['community']

    def get_cost(self, index: str):
        if ' ' in index:
            index = index.split(' ')[0]
        index = re.sub(r'\D', '', index)
        index = int(index)
        return self.data[self.data_order[index-1]]['cost']
        

if __name__ == "__main__":
    src_reader = SrcReader("./src/*.json")
    doc = src_reader.get_document(index="10")
    out = src_reader.get_paragraph(doc, index="1 3")
    print(out)