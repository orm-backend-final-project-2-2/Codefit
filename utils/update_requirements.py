import re
import sys

import requests


def get_requirement_info(line, req_attributes):
    """line에서 requirement 정보를 추출해서 dict로 반환한다."""

    req_info = dict()
    refined_line = [item.strip() for item in line.split("|")[1:-1]]
    for i, attr in enumerate(req_attributes):
        req_info[attr] = refined_line[i]

    return req_info


def create_markdown_table(req_info_list, req_attributes):
    # 테이블 헤더 생성
    headers = "| " + " | ".join(req_attributes) + " |"
    # 구분선 생성
    separator = "|-" + "-|".join(["-" * len(attr) for attr in req_attributes]) + "-|"
    # 테이블 본문 생성
    rows = []
    for req_info in req_info_list:
        row = "| " + " | ".join([req_info[attr] for attr in req_attributes]) + " |"
        rows.append(row)
    # 전체 테이블 합치기
    table = "\n".join([headers, separator] + rows)
    return table


def update_issue(issue_id, issue_body, owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"body": issue_body}
    response = requests.patch(url, headers=headers, json=data)


def check_label_exist(label_name, owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/labels/{label_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True


def create_new_label(label_name, owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    data = {
        "name": label_name,
    }
    response = requests.post(url, headers=headers, json=data)


def create_new_issue(issue_title, issue_body, labels, owner, repo, token):
    if not check_label_exist(labels[0], owner, repo, token):
        create_new_label(labels[0], owner, repo, token)
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"title": issue_title, "body": issue_body, "labels": labels}
    response = requests.post(url, headers=headers, json=data)


def update_feature_requirements_issue(
    issue_title, issue_body, req_info_list, req_attributes, labels
):
    owner = "orm-backend-final-project-2-2"
    repo = "final-project-server"
    token = pat

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/?labels={labels[0]}"
    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.json()["body"]:
        issue_id = response.json()["body"][0]["id"]
        update_issue(issue_id, issue_body, owner, repo, token)
    else:
        create_new_issue(issue_title, issue_body, labels, owner, repo, token)
        return


def update_app_requirements(app_name, req_file):
    """req_file을 읽어서 정보를 map에 저장하고 app_name에 해당하는 issue를 찾아서 업데이트한다."""

    with open(req_file, "r") as f:
        lines = f.readlines()

        req_attributes = [attribute.strip() for attribute in lines[2].split("|")[1:-1]]

        app_requirements_info = dict()

        for line in lines:
            if line.startswith("|"):
                req_info = get_requirement_info(line, req_attributes)
                if req_info["Feature"] != "":
                    current_feature = req_info["Feature"]
                    app_requirements_info[current_feature] = []
                app_requirements_info[current_feature].append(req_info)

        for feature in app_requirements_info:
            issue_title = f"REQ-{app_name}-{feature}"
            labels = [f"req-{app_name}"]
            issue_body = create_markdown_table(
                app_requirements_info[feature], req_attributes
            )

            update_feature_requirements_issue(
                issue_title,
                issue_body,
                app_requirements_info[feature],
                req_attributes,
                labels,
            )


def update_requirements(changed_requirements_file):
    req_file_pattern = re.compile(r"docs/requirements/(.*)_requirements.md")

    match = req_file_pattern.search(changed_requirements_file)
    if match:
        app_name = match.group(1)
        update_app_requirements(app_name, changed_requirements_file)


raw_changed_file = sys.argv[1]
pat = sys.argv[2]

update_requirements(raw_changed_file)
