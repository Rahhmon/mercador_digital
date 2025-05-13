from scrap.facebook import FacebookScraper
from ia_agent.data_extract import MobilePhoneParser
from data_treatment import DataTreatment


if __name__ == '__main__':
    #1. Get all new available facebook available products.
    FacebookScraper.main()
    #2. Clean facebook data
    DataTreatment.main()
    #3. Get important information through I.A
    MobilePhoneParser.main()