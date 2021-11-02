#!/usr/bin/env python3

"""
Add a list of users to a GitHub organisation

Rate limit is 500 per day or 50 if you do not meet certain requirements.

An OAuth access token is needed, see the following URL::
https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token

For more informations see the following URL:
https://docs.github.com/en/free-pro-team@latest/rest/reference/orgs#set-organization-membership-for-a-user
"""

import time
import sys
import argparse
import re
import requests


def read_file(inputfile):
    """
    Read file containing list of email addresses to be added
    """

    try:
        with open(inputfile, 'r', encoding='utf=8') as file:
            content = file.readlines()
            content = [line.strip() for line in content]
    except IOError:
        print('File could not be opened.')
        sys.exit(3)

    return content


def post(content, args):
    """
    Post email addresses to GitHub API, adding them to the named organisation
    """

    invitecount = 0
    for email in content:
        req = requests.post('https://api.github.com/orgs/' + args.org + '/invitations', headers=H, json={"email":email}, auth = (args.username, args.token))
        time.sleep(1)
        print(req.status_code, req.reason)
        print(req.text)
        if req.status_code != 201:
            print("Error occurred. " + str(invitecount) + " have been invited. See error information above.")
            sys.exit(4)
        invitecount+=1
    print("Finished. " + str(invitecount) + " has been invited.")


def filter_email_list(content, args):
    """
    Filter list of provided emails against a given filterdomain
    """

    email_list = content
    regex = "r'\b[A-Za-z0-9._%+-]+@" + args.filterdomain + "\b'"
    filtered_list = []

    for entry in email_list:
        if re.fullmatch(regex, entry):
            filtered_list.append(entry)

    return filtered_list


def get_options():
    """
    Get command-line options
    """

    parser = argparse.ArgumentParser(description='Send Github Organisation invites to a list of user email addresses')
    parser.add_argument("-o", required=True, dest='org', help="The GitHub Organisation to add users to")
    parser.add_argument("-u", required=True, dest='username', help="A GitHub username to authenticate with. This user must have access to add users to the GitHub organisation specified with -o")
    parser.add_argument("-t", required=True, dest='token', help="Your GitHub Personal Access Token")
    parser.add_argument("-f", required=True, dest='inputfile', help="Name of the file containing a list of email addresses to send GitHub organisation invites to. If file is not in the same directory as this script, include full path to file")
    parser.add_argument("--filterdomain", required=False, help="If specified, only emails from filterdomain will be sent invites. Any email addresses in your input file that are not from this domain will be ignored.")
    args=parser.parse_args()

    return args


def main():
    """
    main
    """


    args = get_options()

    content = read_file(args.inputfile)

    if args.filterdomain:
        valid_emails = filter_email_list(content, args)
        post(valid_emails, args)
    else:
        post(content, args)


if __name__ == "__main__" :

    H = {
        'Content-type': 'application/json',
       'Accept' : 'application/vnd.github.v3+json'
    }

    main()
