name: Run Profits_2 Script

on:
  schedule:
    - cron: '0 */4 * * *'  # Runs every 4 hours

jobs:
  run_profits_script_and_save_output:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2
        
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.x
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install selenium beautifulsoup4 pymongo pytz
        
      - name: Run profits.py script and save output
        run: |
          python profits2.py
