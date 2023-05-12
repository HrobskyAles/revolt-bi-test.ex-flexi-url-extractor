"""
Template Component main class.

"""
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager 
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import csv

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
#KEY_API_TOKEN = '#api_token'
#KEY_PRINT_HELLO = 'url_address'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
#REQUIRED_PARAMETERS = [KEY_PRINT_HELLO]
#REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """

        # ####### EXAMPLE TO REMOVE
        # check for missing configuration parameters
        #self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        #self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        #params = self.configuration.parameters
        # Access parameters in data/config.json
        #if params.get(KEY_PRINT_HELLO):
        #    logging.info("Hello World")

        # get last state data/in/state.json from previous run
        previous_state = self.get_state_file()
        logging.info(previous_state.get('some_state_parameter'))
        
        url = 'https://flex.bi/bi/accounts/112/embed/report/12737?embed_token=gye8u4cyp33hs8jf8u2imnn1tupck9q3py3w3no08r9g4n3divf531rzvc0e' 
 
        driver = webdriver.Chrome(service=ChromeService( 
            ChromeDriverManager().install())) 
        
        driver.get(url) 
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "pivot_table")))
        response = driver.page_source

        soup = BeautifulSoup(response, 'html.parser')
        table_element = soup.select_one('[id*="pivot_table_"]')
        table_id = table_element.get('id')
        print(table_id)

        table = soup.find('table', id=table_id)

        headers = []
        for th in table.find_all('th', {'class': 'column_member'}):
            headers.append(th.find('div', {'class': 'member_box'}).text.strip().replace('\n', ' '))


        rows = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            rows.append(row)

        # Create output table (Tabledefinition - just metadata)
        table = self.create_out_table_definition('output.csv', incremental=True)#, primary_key=['timestamp']

        # get file path of the table (data/out/tables/Features.csv)
        out_table_path = table.full_path
        logging.info(out_table_path)

        # DO whatever and save into out_table_path
        with open(table.full_path, mode='wt', encoding='utf-8', newline='') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(headers)
            writer.writerows(rows)
        
    

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})

        # ####### EXAMPLE TO REMOVE END


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
