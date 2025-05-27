from configparser import ConfigParser
import os


def configOpenAI(filename='config.ini', section='openai'):
    # create a parser
    parser = ConfigParser()
    # read config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, filename)
    parser.read(full_path)

 
    # get section, default to openai
    openai = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            openai[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return openai

# if __name__ == "__main__":
#     CONFIG_OPEN_API = configOpenAI()