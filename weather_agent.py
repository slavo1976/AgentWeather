name: Weather Agent

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Inštalácia knižníc
        run: pip install requests openpyxl PyGithub

      - name: Spusti agenta
        env:
          GITHUB_TOKEN: ${{ secrets.WEATHER_TOKEN }}
          GITHUB_USER: slavo1976
        run: python weather_agent.py 2>&1 | tee agent_output.txt

      - name: Odošli email
        if: always()
        env:
          MAIL_USER: ${{ secrets.MAIL_USER }}
          MAIL_PASS: ${{ secrets.MAIL_PASS }}
          STATUS: ${{ job.status }}
        run: python send_email.py
