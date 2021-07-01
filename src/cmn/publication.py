import json
import traceback
import random
from cmn.member import Member
from cmn.author import Author
from cmn.team import Team
import pickle
import time
import os

random.seed(0)

class Publication(Team):
    def __init__(self, id, authors, title, doc_type, year, venue, references, fos, keywords):
        super().__init__(id, authors)
        self.title = title
        self.year = year
        self.doc_type = doc_type
        self.venue = venue
        self.references = references
        self.fos = fos
        self.keywords = keywords
        self.fields = self.set_fields()
        
    # Fill the fields attribute with non-zero weight from FOS
    def set_fields(self):
        fields = []
        for field in self.fos:
            if field["w"] != 0.0:
                fields.append(field["name"].replace(" ", "_"))
        # Extend the fields with keywords
        if len(self.keywords) != 0:
            fields.extend(self.keywords.replace(" ", "_"))
        return fields
    
    def get_fields(self):
        return self.fields

    def get_skills(self):
        return self.get_fields()

    @staticmethod
    def read_data(data_path, topn=None):
        counter = 0
        teams = {}
        all_members = {}
        # input_data = []
        # output_data = []
        output_name = "_".join(data_path.split("/")[-1].split(".")[:-1])
        output_pickle = f'../data/preprocessed/{output_name}/teams.pickle'

        start_time = time.time()
        try:
            with open(output_pickle, 'rb') as infile:
                print("Loading the pickle.")
                all_members, teams = pickle.load(infile)
                print(f"It took {time.time() - start_time} seconds to load from the pickle.")
                return all_members, teams
        except:
            with open(data_path, "r", encoding='utf-8') as jf:
                # Skip the first line
                jf.readline()
                while True:
                    try:
                        # Read line by line to not overload the memory
                        line = jf.readline()
                        if not line or (topn and counter >= topn):
                            break

                        jsonline = json.loads(line.lower().lstrip(","))

                        # Retrieve the desired attributes
                        id = jsonline['id']
                        title = jsonline['title']
                        year = jsonline['year']
                        type = jsonline['doc_type']
                        venue = jsonline['venue'] if 'venue' in jsonline.keys() else None
                        references = jsonline['references'] if 'references' in jsonline.keys() else []
                        keywords = jsonline['keywords'] if 'keywords' in jsonline.keys() else []

                        # a team must have skills and members
                        if 'fos' in jsonline.keys(): fos = jsonline['fos']
                        else: continue  # fos -> skills
                        if 'authors' not in jsonline.keys(): continue

                        members = []
                        for auth in jsonline['authors']:

                            # Retrieve the desired attributes
                            member_id = auth['id']
                            member_name = auth['name'].replace(" ", "_")

                            if 'org' in auth.keys():
                                member_org = auth['org'].replace(" ", "_")
                            else:
                                member_org = ""

                            if member_id not in all_members.keys():
                                member = Author(member_id, member_name, member_org)
                                all_members[member_id] = member
                            else:
                                member = all_members[member_id]
                            members.append(member)

                            # member = Author(member_id, member_name, member_org)
                            # members.append(member)
                            # if member_id not in members.keys():
                            #     members[member_id] = member

                        team = Publication(id, members, title, year, type, venue, references, fos, keywords)
                        teams[team.id] = team

                        # input_data.append(" ".join(team.get_skills()))
                        # output_data.append(" ".join(team.get_members_names()))

                        counter += 1
                        if counter % 10000 == 0:
                            print(f"{counter} instances have been loaded, and {time.time() - start_time} seconds has passed.")

                    except:  # ideally should happen only for the last line ']'
                        print(f'ERROR: There has been error in loading json line `{line}`!\n{traceback.format_exc()}')
                        continue
                        # raise
            print(f"It took {time.time() - start_time} seconds to load the data.")
            write_time = time.time()
            with open(output_pickle, "wb") as outfile:
                pickle.dump((all_members, teams), outfile)
            print(f"It took {time.time() - write_time} seconds to pickle the data")
            print(f"It took {time.time() - start_time} seconds to load the data and pickle it.")
        return all_members, teams