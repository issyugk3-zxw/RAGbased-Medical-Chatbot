import json
import os
import re
import py2neo
from tqdm import tqdm
import argparse


# 导入普通实体
def import_entity(client, type, entity):
    def create_node(client, type, name):
        order = """create (n:%s{名称:"%s"})""" % (type, name)
        client.run(order)

    print(f"正在导入{type}类数据")
    for en in tqdm(entity):
        create_node(client, type, en)


# 导入疾病类实体
def import_disease_data(client, type, entity):
    print(f"正在导入{type}类数据")
    for disease in tqdm(entity):
        node = py2neo.Node(
            type,
            名称=disease["名称"],
            疾病简介=disease["疾病简介"],
            疾病病因=disease["疾病病因"],
            预防措施=disease["预防措施"],
            治疗周期=disease["治疗周期"],
            治愈概率=disease["治愈概率"],
            疾病易感人群=disease["疾病易感人群"],
        )
        client.create(node)


def create_all_relationship(client, all_relationship):
    def create_relationship(client, type1, name1, relation, type2, name2):
        order = """match (a:%s{名称:"%s"}),(b:%s{名称:"%s"}) create (a)-[r:%s]->(b)""" % (
            type1,
            name1,
            type2,
            name2,
            relation,
        )
        client.run(order)

    print("正在导入关系.....")
    for type1, name1, relation, type2, name2 in tqdm(all_relationship):
        create_relationship(client, type1, name1, relation, type2, name2)


if __name__ == "__main__":
    # 连接数据库的一些参数
    parser = argparse.ArgumentParser(description="通过medical.json文件,创建一个知识图谱")
    parser.add_argument(
        "--website", type=str, default="http://localhost:7687", help="neo4j的连接网站"
    )
    parser.add_argument("--user", type=str, default="neo4j", help="neo4j的用户名")
    parser.add_argument("--password", type=str, default="neo4j123456", help="neo4j的密码")
    parser.add_argument("--dbname", type=str, default="neo4j", help="数据库名称")
    args = parser.parse_args()

    # 连接...
    client = py2neo.Graph(
        "bolt://localhost:7687", auth=(args.user, args.password), name=args.dbname
    )

    # 将数据库中的内容删光
    is_delete = input("注意:是否删除neo4j上的所有实体 (y/n):")
    if is_delete == "y":
        client.run("match (n) detach delete (n)")

    with open("./data/diseases.json", "r", encoding="utf-8") as f:
        all_data = json.load(f)

    # 所有实体
    all_entity = {
        "疾病": [],
        "药物": [],
        "食物": [],
        "食谱": [],
        "检查手段": [],
        "一级科室": [],
        "二级科室": [],
        "其他": [],
        "症状": [],
        "治疗方案": [],
    }

    # 实体间的关系
    relationship = []
    for i, data in enumerate(all_data):
        if len(data) < 3:
            continue

        disease_name = data.get("name", "")
        all_entity["疾病"].append(
            {
                "名称": disease_name,
                "疾病简介": data.get("desc", ""),
                "疾病病因": data.get("cause", ""),
                "预防措施": data.get("prevent", ""),
                "治疗周期": data.get("cure_lasttime", ""),
                "治愈概率": data.get("cured_prob", ""),
                "疾病易感人群": data.get("easy_get", ""),
            }
        )

        drugs = data.get("common_drug", []) + data.get("recommand_drug", [])
        all_entity["药物"].extend(drugs)  # 添加药品实体
        if drugs:
            relationship.extend(
                [("疾病", disease_name, "疾病使用药品", "药品", durg) for durg in drugs]
            )

        do_eat = data.get("do_eat", [])
        recommend_eat = data.get("recommand_eat", [])
        no_eat = data.get("not_eat", [])
        all_entity["食物"].extend(do_eat + no_eat)
        all_entity["食谱"].extend(recommend_eat)
        if do_eat:
            relationship.extend(
                [("疾病", disease_name, "疾病宜吃食物", "食物", f) for f in do_eat]
            )
        if recommend_eat:
            relationship.extend(
                [("疾病", disease_name, "疾病推荐食谱", "食物", f) for f in do_eat]
            )
        if no_eat:
            relationship.extend(
                [("疾病", disease_name, "疾病忌吃食物", "食物", f) for f in no_eat]
            )

        check = data.get("check", [])
        all_entity["检查手段"].extend(check)
        if check:
            relationship.extend(
                [("疾病", disease_name, "疾病所需检查", "检查手段", ch) for ch in check]
            )

        cure_department = data.get("cure_department", [])

        if cure_department:
            primary_dept = cure_department[0]

            if len(cure_department) > 1:
                all_entity["一级科室"].append(primary_dept)
                secondary_dept = cure_department[1]
                all_entity["二级科室"].append(secondary_dept)

                relationship.append(
                    ("疾病", disease_name, "疾病所属科室", "二级科室", secondary_dept)
                )

                relationship.append(
                    ("二级科室", secondary_dept, "科室归属", "一级科室", primary_dept)
                )
            else:
                all_entity["其他"].append(primary_dept)
                relationship.append(("疾病", disease_name, "疾病所属科室", "其他", primary_dept))
        symptom = data.get("symptom", [])
        for i, sy in enumerate(symptom):
            if symptom[i].endswith("..."):
                symptom[i] = symptom[i][:-3]
        all_entity["症状"].extend(symptom)
        if symptom:
            relationship.extend(
                [("疾病", disease_name, "疾病的症状", "症状", sy) for sy in symptom]
            )

        cure_way = data.get("cure_way", [])
        if cure_way:
            for i, cure_w in enumerate(cure_way):
                if isinstance(cure_way[i], list):
                    cure_way[i] = cure_way[i][0]  # glm处理数据集偶尔有格式错误
            cure_way = [s for s in cure_way if len(s) >= 2]
            all_entity["治疗方案"].extend(cure_way)
            relationship.extend(
                [("疾病", disease_name, "治疗方法", "治疗方案", cure_w) for cure_w in cure_way]
            )

        acompany_with = data.get("acompany", [])
        if acompany_with:
            relationship.extend(
                [
                    ("疾病", disease_name, "疾病并发疾病", "疾病", disease)
                    for disease in acompany_with
                ]
            )

    for i in range(len(relationship)):
        if len(relationship[i]) != 5:
            print(relationship[i])
    relationship = list(set(relationship))
    all_entity = {k: (list(set(v)) if k != "疾病" else v) for k, v in all_entity.items()}

    # 将属性和实体导入到neo4j上,注:只有疾病有属性，特判
    for k in all_entity:
        if k != "疾病":
            import_entity(client, k, all_entity[k])
        else:
            import_disease_data(client, k, all_entity[k])
    create_all_relationship(client, relationship)
