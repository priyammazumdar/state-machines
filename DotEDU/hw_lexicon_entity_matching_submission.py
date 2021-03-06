from emora_stdm import KnowledgeBase, DialogueFlow, NatexNLG, Macro, NatexNLU
from enum import Enum, auto
from typing import Set, Optional, List

from nltk.corpus.reader import Synset
from nltk.corpus import wordnet as wn
import random, re


# TODO: Update the State enum as needed
class State(Enum):
    START = auto()
    PROMPT = auto()
    YES_COLLEGE = auto()
    COLLEGE = auto()
    WHICH_COLLEGE = auto()
    GRADUATE = auto()
    GAP = auto()
    NO_COLLEGE = auto()
    ASK_GO_TO_COLLEGE = auto()
    ASK_ALTERNATIVE = auto()
    MILITARY = auto()
    CAREER = auto()
    PROSPECTIVE = auto()
    UNSURE_COLLEGE = auto()
    UNSURE_FEELS = auto()
    ENROLL = auto()
    WHICH_YEAR = auto()
    FIRST_YEAR = auto()
    SECOND_YEAR = auto()
    THIRD_YEAR = auto()
    FOURTH_YEAR = auto()
    IDK_YEAR = auto()
    FIRST_TRANSITION = auto()
    GOOD_TRANS = auto()
    NOTGOOD_TRANS = auto()
    IDK_TRANS = auto()
    ERROR_TRANS = auto()
    FAVORITE_COLLEGE = auto()
    OPPORTUNITIES = auto()
    OPP_FURTHER = auto()
    FRIENDS = auto()
    FRIEND_CONT = auto()
    YES_FRIEND = auto()
    NO_FRIEND = auto()
    ERR_FRIEND = auto()
    FREEDOM = auto()
    RESOURCES = auto()
    PARTIES = auto()
    DIVERSITY = auto()
    PEOPLE = auto()
    DORM = auto()
    DATING = auto()
    DRINKING = auto()
    CITY = auto()
    FOOD = auto()
    SPORTS = auto()
    GREEK = auto()
    THEATER = auto()
    RESEARCH = auto()
    DANCE = auto()
    SING = auto()
    MUSIC = auto()
    ART = auto()
    VOLUNTEER = auto()
    SUSTAINABILITY = auto()
    ONCAMPUS_JOB = auto()
    ERR_OPP = auto()
    ACADEMICS = auto()
    IDKFAVE_COLLEGE = auto()
    YOURFAVE_COLLEGE = auto()
    ERR_FAVECOLLEGE = auto()
    KNOW_COLLEGE = auto()
    ASK_STATUS = auto()
    COLLEGE_STATUS = auto()
    IDKTHATSCHOOL = auto()
    YES_GRADUATE = auto()
    WHICH_ALMAMATER = auto()
    ALMAMATER = auto()
    KNOW_ALMA = auto()
    IDK_ALMA = auto()
    NO_GRADUATE = auto()
    DROP_OUT = auto()
    CO_OP = auto()
    BREAK = auto()
    WHICH_NOCOLLEGE = auto()
    PLANS = auto()
    COOP_LENGTH = auto()
    BREAK_LENGTH = auto()
    REFUSE_COLLEGE = auto()
    RETURN_COLLEGE = auto()
    BREAK_TIME = auto()
    RETURN_FEEL = auto()
    NEG_EMOTION = auto()
    POS_EMOTION = auto()
    EXCITED_EMOTION = auto()
    COMMENT = auto()
    THANKS = auto()
    ALTERNATIVE = auto()
    INTERESTED_GAP = auto()
    DECIDE_MILITARY = auto()
    DECIDE_MILITARY_NEXT = auto()
    DECISION_KNOW = auto()
    KNOWFUTURE_COLLEGE = auto()
    NOKNOW_COLLEGE = auto()
    EXCITED_COLLEGE = auto()
    MOVEON_GAP = auto()
    IDK_GAP = auto()
    SUGGEST_HELP = auto()
    NOHELP_WANTED = auto()
    HELP_WANTED = auto()
    IDK_HELP = auto()
    FIGUREIDK_WHY = auto()
    ASK_AWAY_FAMILY = auto()
    STAY_WITH_FAMILY = auto()
    NOT_STAY_WITH_FAMILY = auto()
    ASK_CURRENT_STATE = auto()
    RESPOND_CURRENT_STATE = auto()
    FIND_EXPENSE = auto()
    NOPREF_EXPENSE = auto()
    ASK_BUDGET = auto()
    ASK_AID = auto()
    NO_BUDGETRESPONSE = auto()
    FIND_AID = auto()
    RECOMMEND_AID = auto()
    GO_CHEAPSCHOOL = auto()
    FINAID_OFFICE = auto()
    REC_FAFSA = auto()
    RECOMMEND_SCHOLARSHIP = auto()
    MORE_SCHOLARSHIP = auto()
    REC_SCHOLARSHIP = auto()
    SECRET_SCHOLARSHIP = auto()
    COMMUNITYCOLL = auto()
    ASKFIN_OFFICE = auto()
    BUDGET_RESPONSE = auto()
    FIND_LEARNSTYLE = auto()
    NOPREFSTYLE = auto()
    RESPOND_LEARNSTYLE = auto()
    SCHOOL_SIZE = auto()
    ASK_ACTIVITIES = auto()
    SCHOOL_SETTING = auto()
    SCHOOL_LOCATION = auto()
    PROBE_ACTIVITY = auto()
    FIND_ACTIVITY = auto()
    ASK_LOCATION = auto()
    RESPOND_LOCATION = auto()
    NOPREF_CITY = auto()
    SALIENT_Q = auto()
    SALIENCY = auto()
    FINALCOLLEGES = auto()
    UNSURE_OKAY = auto()
    UNSURE_OKAY_GENERIC = auto()
    UNSURE_EMOTION = auto()
    ERROR_TRANSITION = auto()
    ERROR_YEAR = auto()
    END = auto()
    ERR = auto()


# TODO: create the ontology as needed
# Reads in the master list of colleges
college_file_name = 'college_list_master.txt'
college_names = []
college_name_attr = 'institution name'

##############################
state_attr = 'in state'
public_attr = 'public'
setting_attr = 'setting'
hbc_attr = 'historically black'
tribal_attr = 'tribal'
ivy_league_attr = 'Ivy League'
size_attr = 'size'
# This dictionary contains attribute descriptions as keys and tuples as entries, where each tuple contains two
# values. The first value of the tuple is the actual attribute name of the information specified in the key. The second
# value of the tuple is None if the attribute is non-binary (i.e. the value should be saved regardless of the
# information). Otherwise, the second value of the tuple is a string that corresponds to the value being true in the
# table (e.g. 'Yes'/'No' or '1'/'0')
attribute_names = {state_attr: ('HD2018.State abbreviation', None),
                   public_attr: ('HD2018.Control of institution', 'Public'),
                   setting_attr: ('Setting', None),
                   hbc_attr: ('HD2018.Historically Black College or University', 'Yes'),
                   tribal_attr: ('HD2018.Tribal college', 'Yes'),
                   ivy_league_attr: ('isIvy', 'Yes'),
                   size_attr: ('Size', None)}
##############################

important_attributes = {name[0]: {} if name[1] is None else (set(), name[1]) for attr, name in attribute_names.items()}

with open(college_file_name, 'r') as college_file:
    lines = college_file.readlines()
    college_data_headers = lines[0].split('\t')
    college_name_column = 0

    for column_index, attribute in enumerate(college_data_headers):
        if attribute == college_name_attr:
            college_name_column = column_index
            for row_index in range(1, len(lines)):
                line = lines[row_index].split('\t')
                college_names.append(line[college_name_column])

    for column_index, attribute in enumerate(college_data_headers):
        if attribute in important_attributes:
            if type(important_attributes[attribute]) == dict:
                for row_index in range(1, len(lines)):
                    line = lines[row_index].split('\t')
                    value = line[column_index].lower()
                    if value in important_attributes[attribute]:
                        important_attributes[attribute][value].add(line[college_name_column])
                    else:
                        important_attributes[attribute][value] = {line[college_name_column]}
            else:
                for row_index in range(1, len(lines)):
                    line = lines[row_index].split('\t')
                    value = line[column_index]
                    if value == important_attributes[attribute][1]:
                        important_attributes[attribute][0].add(line[college_name_column])

##########
# Emotions
##########
positive_emotions = frozenset({"good", "happy", "joy", "joyful", "excited", "optimistic", "optimism", "relieved",
                               "ecstatic", "glee", "gleeful", "great", "relief", "relieved", "amazing", "excellent",
                               "fantastic", "extraordinary", "outstanding", "peace", "peaceful", "nice", "fortunate",
                               "bliss", "blissful", "positive", "cheery", "cheerful", "comfortable", "grateful",
                               "splendid", "confident", "terrific", "incredible", "tremendous", "elated", "lovely",
                               "wonderful", "eager"})
negative_emotions = frozenset({"sad", "guilty", "bad", "depressed", "depression", "angry", "anger", "jealous",
                               "jealous", "afraid", "fear", "scared", "lonely", "alone", "abysmal", "anxious", "awful",
                               "terrible", "horrible", "atrocious", "broken", "crazy", "confused", "damaged",
                               "disgusting", "distress", "distressed", "dread", "dreadful", "enraged", "evil", "foul",
                               "filthy", "fright", "frightened", "grim", "gross", "grave", "hurt", "horrendous", "ill",
                               "sick", "sickened", "lousy", "naughty", "nauseous", "negative", "poor", "pain",
                               "painful", "sorry", "stupid", "tense", "woe", "woeful", "worried", "yucky"})
emotions_set = {positive_emotions, negative_emotions}

##########
# States
##########
us_states = frozenset({'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware',
                       'district of columbia', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
                       'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
                       'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey',
                       'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
                       'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah',
                       'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming'})
us_states_dict = {us_states: ('in state', state_attr, None)}

##########
# Tuition
##########
worried_finances = frozenset({"yes", "yeah", "yep", "correct", "ye", "indeed", "of course", "absolutely", "i do",
                              "sure", "i guess", "sounds good", "of course", "okay", "ok", "o.k.", "yup",
                              "affirmative"})
consider_price_dict = {worried_finances: ("affordable", None)}

high_price = frozenset({"expensive", "a lot", "a bunch", "everything", "anything", "any", "lots"})
medium_price = frozenset({"medium", "not too much", "not too little", "average", "normal", "in between", "not a lot"})
low_price = frozenset({"cheap", "as low as possible", "free", "cannot afford", "not much", "little", "small"})
tuition_dict = {high_price: ("high, medium or low tuition", None), medium_price: ("medium to low tuition", None),
                low_price: ("low tuition", None)}

##########
# Learn style
##########
small_lecture = frozenset({"personal attention", "small classes", "small", "few classmates", "few", "essay", "essays",
                           "writing", "one on one", "one-on-one", "little", "close"})
medium_lecture = frozenset({"medium", "between", "mixed", "middle", "average", "moderate", "intermediate",
                            "neutral", "so so", "so-so", "normal", "fair"})
large_lecture = frozenset({"large", "multiple choice", "big", "memorization", "memorize", "on my own", "self", "huge",
                           "giant", "massive"})
learn_style_dict = {small_lecture: ("small lectures", size_attr, "small"),
                    medium_lecture: ("medium-sized lectures", size_attr, "medium"),
                    large_lecture: ("large lectures", size_attr, "large")}

##########
# Location
##########
city = frozenset({"city", "diverse", "fast", "party", "parties", "partying", "club", "clubbing", "urban"})
suburb = frozenset({"suburb", "suburban", "suburbs"})
rural = frozenset({"rural", "farm", "farming", "barn", "hills", "pasture", "husbandry", "animal", "animals"})
town = frozenset({"town"})
# beach = frozenset({"beach", "sand", "palm trees", "surf", "surfing", "surfboard", "ocean", "sea", "wave", "waves",
#                    "boat", "sail", "yacht", "boating", "sailing", "california", "scuba dive", "scuba diving",
#                    "snorkeling", "snorkel", "sea diving", "sea dive", "deep dive", "deep diving", "salt water",
#                    "marine"})
location_dict = {city: ("city setting", setting_attr, "city"), suburb: ("suburban setting", setting_attr, "suburb"),
                 rural: ("rural setting", setting_attr, "rural"), town: ("town setting", setting_attr, "town")}

##########
# Saliency
##########
state_school = frozenset({"my state", "in state", "state school", "flagship", "public", "state"})
hbc = frozenset({"hbc", "historically black", "african american", "african americans", "black college", "black"})
tribal = frozenset({"tribal", "native american", "tribe"})
ivy_league = frozenset({"ivy", "ivy league", "brown", "columbia", "yale", "harvard", "dartmouth", "cornell", "harvard",
                        "princeton", "upenn", "pennsylvania"})
saliency_dict = {state_school: ("public state school", public_attr), hbc: ("historically black school", hbc_attr),
                 tribal: ("tribal school", tribal_attr), ivy_league: ("Ivy League school", ivy_league_attr)}


##########
# Wordnet Synonyms
##########
def synonyms(word: str, pos: Optional[str] = None, count: Optional[int] = 0) -> Set[str]:
    syns = set()

    for synset in wn.synsets(word, pos):
        for lemma in synset.lemmas():
            if lemma.count() >= count:
                syns.add(lemma.name())

    return syns


##########
##########

ontology = {
    "ontology": {
        "ontUSStates":
            [state.lower() for state in us_states],
        "ontCollegeNames":
            college_names,
        "ontEmotion":
            [j for i in emotions_set for j in i],
        "ontPosEmotion":
            list(positive_emotions),
        "ontNegEmotion":
            list(negative_emotions),
        "ontConsiderPrice":
            [j for i in consider_price_dict for j in i],
        "ontTuition":
            [j for i in tuition_dict for j in i],
        "ontLearnStyle":
            [j for i in learn_style_dict for j in i],
        "ontSchoolLocation":
            [j for i in location_dict for j in i],
        "ontSaliency":
            [j for i in saliency_dict for j in i]
    }
}

knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge)

df.add_system_transition(State.START, State.PROMPT, '"Hi, have you ever been to college?"')

######################################
# Natex
# TODO: Finish creating all natex.
######################################
yes_natex = r"[{yes, yeah, yep, correct, ye, indeed, of course, absolutely, i do, sure, i guess, sounds good, " \
            r"of course, okay, ok, o.k., yup, affirmative}]"
no_natex = r"[{no, none, nothing, dont use, dont really use, never, nope, nah, negative, not really}]"
idk_natex = r"[{no preference, i dont know, no favorite, neither, i dont have one}]"
yes_no_idk_natex = r"[{yes, yeah, yep, correct, ye, indeed, of course, absolutely, i do, sure, i guess, sounds good," \
                   r"of course, no, none, nothing, dont use, dont really use, never, nope, nah, no preference," \
                   r"i dont know, no favorite, neither, i dont have one}]"
college_natex = r"[{college, university},{currently, right now, now, i am in, im in}]"
collegename_natex = r"[$collegename=#ONT(ontCollegeNames)]"
firstyear_natex = r"[{first-yearr, first-year, freshman, first, first year}]"
secondyear_natex = r"[{second, second year, second-year, sophomore}]"
thirdyear_natex = r"[{third, third year, third-year, junior}]"
fourthyear_natex = r"[{fourth, fourth year, fourth-year, senior}, {college, university, grad, med, law, vet, dental}]"
graduate_natex = r"[{graduate, graduated, alumni, finish, finished, over}]"
gap_natex = r"[{gap, break, time off}]"''
military_natex = r"[{military, army, navy, marine, marines, coast guard, air force}]"
career_natex = r"[{work, working, job, career}]"
prospective_natex = r"[{high school, highschool, senior, thinking about it, planning to, plan, plan to, applying, " \
                    r"want to, apply, want to go, prospective}]"
yesprospective_natex = yes_natex + prospective_natex
almamater_natex = r"[$alma=#ONT(ontCollegeNames)]"
dropout_natex = r"[{drop, drop out, withdraw, withdrawal, leave, dropped out}]"
coop_natex = r"[{co-op, coop, cooperative, co op}]"
break_natex = r"[{break, pause}]"
time_natex = r"[{year, years, month, months, week, weeks, day, days, hour, hours, minute, minutes, second, " \
             r"seconds, january, february, march, april, may, june, july, august, september, october, november, " \
             r"december}]"
emotion_natex = r"[$emotion=#ONT(ontEmotion)]"
negemotion_natex = r"[$negemotion=#ONT(ontNegEmotion)]"
posemotion_natex = r"[$posemotion=#ONT(ontPosEmotion)]"
thank_natex = r"[{thanks, thank you, many thanks, thankful}]"
travel_natex = r"[{travel, explore, see the world, vacation}]"
financial_natex = r"[{money, earn money, make money, make some money, earn some money}]"
volunteer_natex = r"[{volunteer, volunteering, community service}]"
passion_natex = r"[{passionate, passion, love, enjoy}]"
family_natex = r"[{family, familial}]"
rotc_natex = r"{[{rotc, reserve officers' training corps, reserve officers training corps}]"
rejected_natex = r"[{rejected, denied, not accepted, turned down, rescind, rescinded}]"
opportunity_natex = r"[{opportunity, opportunities, potential, potentiality, potentials}]"
familybus_natex = r"[{family business, family-owned, family-owned business}]"
familypressure_natex = r"[{pressure, parents, family}]"
independence_natex = r"[{independent, independence}]"
lifeexperience_natex = r"[{experience, life experience, gain experience, experiential}]"
location_natex = r"[{location, place}]"
athletics_natex = r"[{athletic, athletics, sport, sports}]"

######################################
# Determining post-high school graduation event.
######################################
df.add_user_transition(State.PROMPT, State.YES_COLLEGE, yes_natex)
df.add_user_transition(State.PROMPT, State.COLLEGE, college_natex)
#df.add_user_transition(State.PROMPT, State.KNOW_COLLEGE, collegename_natex)
df.add_user_transition(State.PROMPT, State.GRADUATE, graduate_natex)
df.add_user_transition(State.PROMPT, State.GAP, gap_natex)
df.add_user_transition(State.PROMPT, State.NO_COLLEGE, no_natex)
df.add_user_transition(State.PROMPT, State.MILITARY, military_natex)
df.add_user_transition(State.PROMPT, State.CAREER, career_natex)
df.add_user_transition(State.PROMPT, State.PROSPECTIVE, prospective_natex)
df.add_user_transition(State.PROMPT, State.UNSURE_COLLEGE, idk_natex)
df.set_error_successor(State.PROMPT, State.ERR)

########################################
# Has college experience
########################################
df.add_system_transition(State.YES_COLLEGE, State.ENROLL, '"Are you currently still in college?"')

# Currently enrolled
df.add_user_transition(State.ENROLL, State.KNOW_COLLEGE, collegename_natex)
df.add_user_transition(State.ENROLL, State.COLLEGE, yes_natex)
df.set_error_successor(State.ENROLL, State.ERR)

df.add_system_transition(State.COLLEGE, State.WHICH_YEAR, '"What year are you in?"')

#df.add_user_transition(State.WHICH_COLLEGE, State.KNOW_COLLEGE, collegename_natex)
#df.set_error_successor(State.WHICH_COLLEGE, State.IDKTHATSCHOOL)
#df.add_system_transition(State.KNOW_COLLEGE, State.END,
                        # '[! $collegename " is a great school. Good luck with the semester."]')
#df.add_system_transition(State.IDKTHATSCHOOL, State.YEAR_IN_SCHOOL2, '"Hm, I don\'t know that school, but it sounds cool. '
                                                         #'What year are you?"')

###################################
# FIRST YEAR
###################################
df.add_user_transition(State.WHICH_YEAR, State.FIRST_YEAR, firstyear_natex)

df.add_system_transition(State.FIRST_YEAR, State.FIRST_TRANSITION, '"First year is exciting! But, how has your '
                                                                   'transition been so far?"')
df.add_user_transition(State.FIRST_TRANSITION, State.GOOD_TRANS, posemotion_natex)
df.add_system_transition(State.GOOD_TRANS, State.FAVORITE_COLLEGE, '[! "I\'m glad it is " $posemotion " ! '
                                                               'What is your favorite part of college so far?"')
df.add_user_transition(State.FAVORITE_COLLEGE, State.OPPORTUNITIES, r"[{opportunity, opportunities, try, new, "
                                                                    r"campus life, explore, organizations, clubs, "
                                                                    r"organization, club}]")

df.add_user_transition(State.FAVORITE_COLLEGE, State.FRIENDS, r"[{friend, friends, connection, relationship, "
                                                              r"connections, relationships}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.SPORTS, r"[{sport, sports}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.GREEK, r"[{greek, frat, sorority, fraternity, greek life}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.THEATER, r"[{theater, act, acting, theatre, drama}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.RESEARCH, r"[{research, lab, thesis}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.DANCE, r"[{dance, dancing, performing arts}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.ART, r"[{art, draw, paint, sketch, sculpt, visual, arts, drawing, "
                                                          r"painting, sculpting, sketching, photo, photography}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.SING, r"[{sing, singing, song, acapella, a capella, choir, "
                                                           r"chorus}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.MUSIC, r"[{instrument, music, orchestra, band, piano, guitar}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.VOLUNTEER, r"[{volunteer, community service, service,"
                                                                r" philanthropy}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.SUSTAINABILITY, r"[{sustainability, garden, sustainable, "
                                                                     r"gardening}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.ONCAMPUS_JOB, r"[{on campus job, on-campus job, working, job, "
                                                                   r"work, working on campus, work on campus, "
                                                                   r"work study}]")

df.add_system_transition(State.OPPORTUNITIES, State.FAVORITE_COLLEGE, '"What types of opportunities '
                                                                 'have you taken advantage of?"')
df.add_system_transition(State.FRIENDS, State.FRIEND_CONT, '"Have you made close friends recently? It\'s okay if you '
                                                           'haven\'t. It can take some time."')
df.add_user_transition(State.FRIEND_CONT, State.YES_FRIEND, yes_natex)
df.add_user_transition(State.FRIEND_CONT, State.NO_FRIEND, no_natex)
df.set_error_successor(State.FRIEND_CONT, State.ERR_FRIEND)

df.add_user_transition(State.FAVORITE_COLLEGE, State.FREEDOM, r"[{freedom, independence, by myself, independent, "
                                                              r"not dependent, no rules, no restrictions, parents}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.RESOURCES, r"[{resources}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.PARTIES, r"[{party, parties, lit, clubbing}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.DIVERSITY, r"[{diversity}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.PEOPLE, r"[{people, environment, meet, meeting, classmates, "
                                                             r"classmate, professor, professors, teachers, teacher}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.DORM, r"[{dorm, dorming, roommate, room, suite, suitemate, "
                                                           r"suite mate, RA, living on campus}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.ACADEMICS, r"[{academics, classes, class, subject, subjects, major, "
                                                                r"minor}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.DATING, r"[{dating, dates, date, boys, girls, love, sex, romance}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.DRINKING, r"[{drinking, alcohol, alc, drinks, drink}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.CITY, r"[{city, location, place, geography, area, town, state}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.FOOD, r"[{food, eat, eating, menu, dishes, dish}]")
df.add_user_transition(State.FAVORITE_COLLEGE, State.IDKFAVE_COLLEGE, idk_natex)
df.add_user_transition(State.FAVORITE_COLLEGE, State.YOURFAVE_COLLEGE, r"[?]")
df.set_error_successor(State.FAVORITE_COLLEGE, State.ERR_FAVECOLLEGE)


#TODO: finish below transitions
df.add_user_transition(State.FIRST_TRANSITION, State.NOTGOOD_TRANS, negemotion_natex)
df.add_user_transition(State.FIRST_TRANSITION, State.IDK_TRANS, idk_natex)
df.set_error_successor(State.FIRST_TRANSITION, State.ERROR_TRANS)

###################################
# SECOND YEAR
###################################
df.add_user_transition(State.WHICH_YEAR, State.SECOND_YEAR, secondyear_natex)


###################################
# THIRD YEAR
###################################
df.add_user_transition(State.WHICH_YEAR, State.THIRD_YEAR, thirdyear_natex)


###################################
# FOURTH YEAR
###################################
df.add_user_transition(State.WHICH_YEAR, State.FOURTH_YEAR, fourthyear_natex)
df.set_error_successor(State.WHICH_YEAR, State.IDK_YEAR)
df.add_system_transition(State.IDK_YEAR, State.WHICH_YEAR, '"Sorry, is that first, second, third, or fourth year?"')






###################################


# Has graduated already
df.add_user_transition(State.ENROLL, State.ASK_STATUS, no_natex)
df.add_system_transition(State.ASK_STATUS, State.COLLEGE_STATUS, '"Have you graduated already?"')
df.add_user_transition(State.COLLEGE_STATUS, State.YES_GRADUATE, yes_natex)
df.add_system_transition(State.YES_GRADUATE, State.WHICH_ALMAMATER, '"Where did you graduate from?"')
df.add_user_transition(State.COLLEGE_STATUS, State.ALMAMATER, almamater_natex)
df.set_error_successor(State.COLLEGE_STATUS, State.ERR)
df.add_user_transition(State.WHICH_ALMAMATER, State.ALMAMATER, collegename_natex)
df.set_error_successor(State.WHICH_ALMAMATER, State.IDK_ALMA)
df.add_system_transition(State.ALMAMATER, State.COMMENT, '[! $collegename " is a great school. '
                                                         'Good luck with the semester!"]')
df.add_system_transition(State.IDK_ALMA, State.END, '"Hm, I don\'t know that school, but it sounds cool. '
                                                    'Good luck with everything!"')

# Something else
df.add_user_transition(State.COLLEGE_STATUS, State.NO_GRADUATE, no_natex)
df.add_system_transition(State.NO_GRADUATE, State.WHICH_NOCOLLEGE, '"If you don\'t mind me asking, why not?"')

df.add_user_transition(State.COLLEGE_STATUS, State.DROP_OUT, dropout_natex)
df.add_user_transition(State.COLLEGE_STATUS, State.CO_OP, coop_natex)
df.add_user_transition(State.COLLEGE_STATUS, State.BREAK, break_natex)

df.add_user_transition(State.WHICH_NOCOLLEGE, State.DROP_OUT, dropout_natex)
df.add_user_transition(State.WHICH_NOCOLLEGE, State.CO_OP, coop_natex)
df.add_user_transition(State.WHICH_NOCOLLEGE, State.BREAK, break_natex)
df.set_error_successor(State.WHICH_NOCOLLEGE, State.ERR)

# Drop-out
df.add_system_transition(State.DROP_OUT, State.PLANS, '"Would you ever consider going back?"')
df.add_user_transition(State.PLANS, State.REFUSE_COLLEGE, no_natex)
df.add_user_transition(State.PLANS, State.RETURN_COLLEGE, yesprospective_natex)
df.add_user_transition(State.PLANS, State.UNSURE_COLLEGE, idk_natex)
df.set_error_successor(State.PLANS, State.ERR)

df.add_system_transition(State.REFUSE_COLLEGE, State.END, '"That\'s okay. College isn\'t for everyone and you '
                                                          'don\'t necessarily need it to be successful. '
                                                          'Good luck with everything though!"')
df.add_system_transition(State.RETURN_COLLEGE, State.COMMENT, '"I bet there is a lot to think about. Either way'
                                                              ' I wish you luck."')

# Co-op
df.add_system_transition(State.CO_OP, State.COOP_LENGTH, '"How long are you planning to be there?"')
df.add_user_transition(State.COOP_LENGTH, State.BREAK_TIME, time_natex)
df.add_user_transition(State.COOP_LENGTH, State.UNSURE_COLLEGE, idk_natex)
df.set_error_successor(State.COOP_LENGTH, State.ERR)

# Break
df.add_system_transition(State.BREAK, State.BREAK_LENGTH, '"When do you plan on going back?"')
df.add_user_transition(State.BREAK_LENGTH, State.REFUSE_COLLEGE, no_natex)
df.add_user_transition(State.BREAK_LENGTH, State.BREAK_TIME, time_natex)
df.add_user_transition(State.BREAK_LENGTH, State.UNSURE_COLLEGE, idk_natex)
df.set_error_successor(State.BREAK_LENGTH, State.ERR)

df.add_system_transition(State.BREAK_TIME, State.RETURN_FEEL, '"Are you excited to eventually go back?"')
df.add_user_transition(State.RETURN_FEEL, State.NEG_EMOTION, negemotion_natex)
df.add_user_transition(State.RETURN_FEEL, State.POS_EMOTION, posemotion_natex)
df.add_user_transition(State.RETURN_FEEL, State.EXCITED_EMOTION, yes_natex)
df.set_error_successor(State.RETURN_FEEL, State.ERR)
df.add_system_transition(State.EXCITED_EMOTION, State.END, '"I\'m happy for you."')
df.add_system_transition(State.NEG_EMOTION, State.COMMENT, '[! "It\'s okay to feel" $negemotion ". I\'m'
                                                           'sure everything will turn out alright."')
df.add_user_transition(State.COMMENT, State.THANKS, thank_natex)
df.set_error_successor(State.COMMENT, State.END)
df.add_system_transition(State.POS_EMOTION, State.COMMENT, '[! "That\'s great that you feel" $posemotion ".'
                                                           'I can\'t wait for you to go back."')
df.add_system_transition(State.THANKS, State.END, '"You\'re welcome! I hope everything works out well for you."')

#########################################
# Has no college experience
#########################################
df.add_system_transition(State.NO_COLLEGE, State.ASK_GO_TO_COLLEGE, '"Are you planning on going to college?"')
df.add_user_transition(State.ASK_GO_TO_COLLEGE, State.PROSPECTIVE, yes_natex)
df.add_user_transition(State.ASK_GO_TO_COLLEGE, State.ASK_ALTERNATIVE, no_natex)
df.set_error_successor(State.ASK_GO_TO_COLLEGE, State.ERR)
df.add_system_transition(State.ASK_ALTERNATIVE, State.ALTERNATIVE, '"What would you like to do, or what are you '
                                                                   'already doing instead?"')

df.add_user_transition(State.ALTERNATIVE, State.GAP, gap_natex)
df.add_user_transition(State.ALTERNATIVE, State.MILITARY, military_natex)
df.add_user_transition(State.ALTERNATIVE, State.CAREER, career_natex)
df.add_user_transition(State.ALTERNATIVE, State.PROSPECTIVE, prospective_natex)
df.set_error_successor(State.ALTERNATIVE, State.ERR)

# GAP YEAR
df.add_system_transition(State.GAP, State.INTERESTED_GAP, '"That\'s cool to take some time off before college. '
                                                          'What are your plans?"')
df.add_user_transition(State.INTERESTED_GAP, State.IDK_GAP, idk_natex)
df.set_error_successor(State.INTERESTED_GAP, State.MOVEON_GAP)
df.add_system_transition(State.MOVEON_GAP, State.COMMENT, '"That sounds like a good plan. Good luck!"')
df.add_system_transition(State.IDK_GAP, State.COMMENT, '"I\'m sure it will all work out in the end. '
                                                       'Good luck with everything!"')

# MILITARY
df.add_system_transition(State.MILITARY, State.DECIDE_MILITARY, '"That is a really respectful decision.'
                                                                'How did you decide to join the military?"')
df.add_user_transition(State.DECIDE_MILITARY, State.DECIDE_MILITARY_NEXT, yes_natex)
df.set_error_successor(State.DECIDE_MILITARY, State.DECIDE_MILITARY_NEXT)
df.add_system_transition(State.DECIDE_MILITARY_NEXT, State.COMMENT, '"I\'m sure people have a lot of different reasons '
                                                                    'for joining the military, but it\'s cool to hear '
                                                                    'your story as well. I wish you luck moving '
                                                                    'forward!"')

# CAREER
df.add_system_transition(State.CAREER, State.COMMENT, '"Yeah, a lot of people choose to go the same route as '
                                                      'you, so you are definitely not alone. I hope you have '
                                                      'a successful career!"')

########################################
# PROSPECTIVE STUDENT
########################################

df.add_system_transition(State.PROSPECTIVE, State.DECISION_KNOW, '"Do you already know where you\'re going for college?"')
#TODO: write a transition if they've decided not to go to college

# Has picked a college already
df.add_user_transition(State.DECISION_KNOW, State.KNOWFUTURE_COLLEGE, yes_natex)
df.add_user_transition(State.DECISION_KNOW, State.EXCITED_COLLEGE, '[$college_name=#NER(org)]')
df.set_error_successor(State.DECISION_KNOW, State.ERR)

df.add_system_transition(State.KNOWFUTURE_COLLEGE, State.DECISION_KNOW, '"That\'s so exciting! Where are you going?"')

df.add_system_transition(State.EXCITED_COLLEGE, State.COMMENT, '[! $college_name " is a great school. '
                                                               'I\'m really excited for you!"')

# Has not picked a college
df.add_user_transition(State.DECISION_KNOW, State.NOKNOW_COLLEGE, no_natex)
df.add_system_transition(State.NOKNOW_COLLEGE, State.SUGGEST_HELP,
                         '"Do you want me to help you start your college search?"')

df.add_user_transition(State.SUGGEST_HELP, State.NOHELP_WANTED, no_natex)
df.add_system_transition(State.NOHELP_WANTED, State.END, '"That\'s alright. Good luck with everything!"')

df.add_user_transition(State.SUGGEST_HELP, State.IDK_HELP, idk_natex)
df.add_system_transition(State.IDK_HELP, State.FIGUREIDK_WHY, '"Are you unsure about attending college?"')
df.add_user_transition(State.FIGUREIDK_WHY, State.UNSURE_COLLEGE, yes_natex)
df.add_user_transition(State.FIGUREIDK_WHY, State.HELP_WANTED, no_natex)
df.set_error_successor(State.FIGUREIDK_WHY, State.ERR)

df.add_user_transition(State.SUGGEST_HELP, State.HELP_WANTED, yes_natex)
df.set_error_successor(State.SUGGEST_HELP, State.ERR)


#########################################
# College recommendation tool
# TODO: Make a robust, holistic, and unique college search and recommendation tool
# TODO: Add states and natexes to dialogue state machine.
# TODO: Add NER and POS TAGS
# TODO: Make sure natex expressions cover all possible cases
# TODO: Create Wordnet Macros
# TODO: Hardcode more
# TODO: Set error successors where possible
#########################################
# Natex List

#########################################
# MACROS
class EmotionMacro(Macro):

    def __init__(self, positive_emotions_set):
        self.positive_emotions = positive_emotions_set

    def run(self, ngrams, variables, args):
        if args[0] in variables:
            emotion = variables[args[0]]
            emotion_response = "It\'s great that you feel {}.".format(emotion) \
                if emotion in self.positive_emotions else "It\'s okay to feel {}.".format(emotion)
        else:
            emotion_response = "Sometimes I feel that way too."
        return emotion_response


class LocationMacro(Macro):

    def run(self, ngrams, variables, args):
        if args[0] in variables:
            location = variables[args[0]]
            response = "I'm more of a {} bot myself".format(location)
        elif args[1] in variables:
            activity = variables[args[1]]
            response = "Sometimes I like {} too".format(activity)
        else:
            response = "Hmm, interesting"
        return "{}. What kind of reputation do you hope your future school to have?".format(response)


class CollegeRecommenderMacro(Macro):

    def __init__(self, dict_tuple_param, attribute_names_param, important_attributes_param):
        self.dict_tuple = dict_tuple_param
        self.attribute_names = attribute_names_param
        self.important_attributes = important_attributes_param

    def run(self, ngrams, variables, args):
        criteria = [None] * len(self.dict_tuple)
        found_criteria: bool = False

        for i, arg in enumerate(args):
            if arg in variables:
                criteria[i] = variables[arg]
                found_criteria = True

        if not found_criteria:
            return "I\'m sorry. I couldn\'t understand your specified college criteria."

        result = "Based on your preferences, I think you would be " \
                 "interested in a school with the following qualities:\n"

        college_sets = []

        for i, crit in enumerate(criteria):
            if crit is not None:
                for word_set, label in self.dict_tuple[i].items():
                    if crit in word_set:
                        result += label[0]
                        if label[1] is None:
                            result += " (*search for specified criteria not yet implemented*)\n"
                        else:
                            result += "\n"
                            attribute_name = self.attribute_names[label[1]][0]
                            set_data = self.important_attributes[attribute_name]
                            if type(set_data) == tuple:
                                colleges = set_data[0]
                                college_sets.append(colleges)
                            elif type:
                                this_key = self.dict_tuple[i][word_set][2]
                                colleges = set_data[crit] if this_key is None \
                                    else set_data[self.dict_tuple[i][word_set][2]]
                                college_sets.append(colleges)
                        break

        if college_sets:
            matching_colleges = college_sets[0]
            for college_list_index in range(1, len(college_sets)):
                matching_colleges = matching_colleges.intersection(college_sets[college_list_index])
            if not matching_colleges:
                return "{}I can\'t seem to find any colleges that match all of your criteria".format(result)
            elif len(matching_colleges) > 5:
                matching_colleges = random.sample(matching_colleges, 5)
        else:
            return "{}I can\'t seem to find any colleges that match all of your criteria".format(result)

        result += "Here are some colleges that fit those criteria:"
        for college in matching_colleges:
            result += "\n{}".format(college)

        return result


#########################################
# Dialogue States
df.add_system_transition(State.HELP_WANTED, State.ASK_AWAY_FAMILY,
                         '"How would it make you feel to be away from your family?"')

# States to be made for Homework2
# 1. IN-STATE/OUT-STATE/NO-PREF: How would you feel about being away from your family? (POS:Adj)
# Evaluated as a positive, negative, or neutral emotion by the macro
df.add_user_transition(State.ASK_AWAY_FAMILY, State.STAY_WITH_FAMILY, r"[$stateEmotion=#ONT(ontNegEmotion)]")
df.add_user_transition(State.ASK_AWAY_FAMILY, State.NOT_STAY_WITH_FAMILY, r"[$stateEmotion=#ONT(ontPosEmotion)]")
df.set_error_successor(State.ASK_AWAY_FAMILY, State.RESPOND_CURRENT_STATE)

df.add_system_transition(State.NOT_STAY_WITH_FAMILY, State.FIND_EXPENSE,
                         NatexNLG('[! #EmotionMacro(stateEmotion) "Are you worried about finances at all?"]',
                                  macros={'EmotionMacro': EmotionMacro(positive_emotions)}))
df.add_system_transition(State.STAY_WITH_FAMILY, State.ASK_CURRENT_STATE,
                         NatexNLG('[! #EmotionMacro(stateEmotion) "Which state do you live in?"]',
                                  macros={'EmotionMacro': EmotionMacro(positive_emotions)}))

df.add_user_transition(State.ASK_CURRENT_STATE, State.RESPOND_CURRENT_STATE, r"[$currentState=#ONT(ontUSStates)]")
df.set_error_successor(State.ASK_CURRENT_STATE, State.RESPOND_CURRENT_STATE)

df.add_system_transition(State.RESPOND_CURRENT_STATE, State.FIND_EXPENSE, '"Interesting. Are you worried about '
                                                                          'finances at all?"')

# 2. EXPENSIVE/MEDIUM/CHEAP/NO-PREF: Are you worried about finances at all?;
# Healthy discussion about finances
df.add_user_transition(State.FIND_EXPENSE, State.ASK_AID, r"[$worriedFinances=#ONT(ontConsiderPrice)]")
df.set_error_successor(State.FIND_EXPENSE, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.ASK_AID, State.FIND_AID, '"Yeah, I know that higher education can get really '
                                                        'expensive, so I understand. A lot of people are in the '
                                                        'same boat, but many students can qualify for monetary '
                                                        'aid. Have you looked into that?"')

df.add_user_transition(State.FIND_AID, State.RECOMMEND_AID, no_natex)
df.add_user_transition(State.FIND_AID, State.GO_CHEAPSCHOOL, r"[{not enough, need more}]")
df.add_user_transition(State.FIND_AID, State.FINAID_OFFICE, r"[{financial aid package, aid package, aid letter, "
                                                            r"financial letter, financial aid office, financial office,"
                                                            r"aid office, college sent me a, college sent me an, "
                                                            r"school sent me a, school sent me an}]")
df.set_error_successor(State.FIND_AID, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.RECOMMEND_AID, State.REC_FAFSA, '"My biggest piece of advice for you would be to apply '
                                                               'for FAFSA online. Based on you or your family\'s '
                                                               'income,'
                                                               ' the school will be able to provide you with '
                                                               'federally funded financial '
                                                               'aid that can help offset your cost for college. This is'
                                                               ' also the only way you\'ll be eligible for work-study '
                                                               'funds or federally subsidized loans. Are you going to'
                                                               ' apply for scholarships?"')

df.add_user_transition(State.REC_FAFSA, State.RECOMMEND_SCHOLARSHIP, no_natex)
df.add_user_transition(State.REC_FAFSA, State.GO_CHEAPSCHOOL, r"[{not enough, need more}]", score=2.0)
df.add_user_transition(State.REC_FAFSA, State.MORE_SCHOLARSHIP, yes_natex)
df.set_error_successor(State.REC_FAFSA, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.RECOMMEND_SCHOLARSHIP, State.REC_SCHOLARSHIP, '"Maybe you qualify for a scholarship. '
                                                                             'Depending on your grades, schools may '
                                                                             'offer merit based aid. You can also '
                                                                             'apply for merit scholarships. Many '
                                                                             'states have state-funded scholarships '
                                                                             'based on grades as well. There are also '
                                                                             'club-based scholarships like for '
                                                                             'athletics or fine arts. Not all '
                                                                             'scholarships require a high GPA, but it '
                                                                             'will take some researching."')

df.add_user_transition(State.REC_SCHOLARSHIP, State.MORE_SCHOLARSHIP, r"[{I can't find, I can't find any more, I can't "
                                                                      r"find any more scholarships, I don't know where "
                                                                      r"to look, I am confused about where to look, "
                                                                      r"I am confused where to look, where to look, "
                                                                      r"already tried, so hard to find, hard to find}]")
df.set_error_successor(State.REC_SCHOLARSHIP, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.MORE_SCHOLARSHIP, State.SECRET_SCHOLARSHIP, '"Some places people forget to look are your'
                                                                           ' high school\'s PTA committee. They usually'
                                                                           ' host scholarships for smaller amounts of'
                                                                           ' money, but every penny counts! Another '
                                                                           'place is employers. Many companies '
                                                                           'have scholarships for their employees or '
                                                                           'children of employees."')

df.add_user_transition(State.SECRET_SCHOLARSHIP, State.GO_CHEAPSCHOOL, r"[{not enough, need more}]")
df.set_error_successor(State.SECRET_SCHOLARSHIP, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.GO_CHEAPSCHOOL, State.COMMUNITYCOLL, '"If you don\'t think scholarships are enough to '
                                                                    'cover your costs, you can look into more '
                                                                    'affordable schools. In-state public schools are '
                                                                    'your best bet, and community colleges can be a '
                                                                    'good idea too. If you decide that you want to '
                                                                    'attend a larger institution with more resources, '
                                                                    'you can always transfer out later. At least you '
                                                                    'saved some money in the beginning."')
df.set_error_successor(State.COMMUNITYCOLL, State.NO_BUDGETRESPONSE)

df.add_system_transition(State.FINAID_OFFICE, State.ASKFIN_OFFICE, '"Don\'t be afraid to contact the financial aid '
                                                                   'offices of any college you have been accepted to '
                                                                   'but is too expensive. Often times, they can help '
                                                                   'you find ways to make their '
                                                                   'college more affordable '
                                                                   'for you or find ways to increase their financial '
                                                                   'aid package. You never know until you try! '
                                                                   'Besides, the worst they can say to you is no."')
df.set_error_successor(State.ASKFIN_OFFICE, State.NO_BUDGETRESPONSE)

# 3. SMALL/MEDIUM/LARGE/NO-PREF: What kind of classroom setting do you learn best in? (POS: Adj); Do you expect to
# participate in a lot of campus activities?
df.add_system_transition(State.NO_BUDGETRESPONSE, State.FIND_LEARNSTYLE, '"So, what kind of classroom setting '
                                                                         'do you learn best in?"')
# Evaluated as small or large classrooms by the macro
df.add_user_transition(State.FIND_LEARNSTYLE, State.SCHOOL_SIZE, r"[$learnStyle=#ONT(ontLearnStyle)]")
df.set_error_successor(State.FIND_LEARNSTYLE, State.SCHOOL_SIZE)

# df.add_system_transition(State.RESPOND_LEARNSTYLE, State.ASK_ACTIVITIES,
#                          '"Do you care about having many opportunities for campus activities and extracurriculars?"')

# df.add_user_transition(State.ASK_ACTIVITIES, State.SCHOOL_SETTING, yes_no_idk_natex)
# df.set_error_successor(State.ASK_ACTIVITIES, State.SCHOOL_SETTING)

df.add_system_transition(State.SCHOOL_SIZE, State.ASK_LOCATION, '"What type of setting would you '
                                                                'want your school to be in?"')

# 4. CITY/SUBURB/RURAL/BEACH/NO-PREF: What kinds of activities do you like to do regularly? (POS: noun, verb)
# Evaluated as city, suburb, rural or beach by the macro
df.add_user_transition(State.ASK_LOCATION, State.RESPOND_LOCATION,
                       r"[$schoolLocation=#ONT(ontSchoolLocation)]", score=2.0)
# df.add_user_transition(State.ASK_LOCATION, State.RESPOND_LOCATION, '[$city_activity=#POS(noun, verb)]')
df.set_error_successor(State.ASK_LOCATION, State.PROBE_ACTIVITY)

df.add_system_transition(State.PROBE_ACTIVITY, State.FIND_ACTIVITY, '"What activity do you like to do regularly?"')
df.add_user_transition(State.FIND_ACTIVITY, State.RESPOND_LOCATION, '[$activity=#POS(noun,verb)]')
df.set_error_successor(State.FIND_ACTIVITY, State.RESPOND_LOCATION)

df.add_system_transition(State.RESPOND_LOCATION, State.SALIENT_Q,
                         NatexNLG('[! #LocationMacro(schoolLocation, activity)]',
                                  macros={'LocationMacro': LocationMacro()}))

# 5. IVY/STATE/HBC/SINGLESEX/TRIBAL/NO-PREF: What do you hope your future classmates to be like? (POS:Adj) Is there
# any particular reputation or characteristic you want your future college to have?
# Evaluated as ivy, state, hbc or tribal by the macro
df.add_user_transition(State.SALIENT_Q, State.SALIENCY, r"[$saliency=#ONT(ontSaliency)]")
df.set_error_successor(State.SALIENT_Q, State.SALIENCY)

# '"There are a lot of factors to consider before thinking about college, '
# 'but based on our conversation, I think you would enjoy a school. Some '
# 'examples are . How does that sound?"'

dict_tuple = (us_states_dict, consider_price_dict, learn_style_dict, location_dict, saliency_dict)

df.add_system_transition(State.SALIENCY, State.FINALCOLLEGES,
                         NatexNLG('[! #CollegeRecommenderMacro(currentState, worriedFinances, '
                                  'learnStyle, schoolLocation, saliency)]',
                                  macros={'CollegeRecommenderMacro': CollegeRecommenderMacro(dict_tuple,
                                                                                             attribute_names,
                                                                                             important_attributes)}))

df.add_user_transition(State.FINALCOLLEGES, State.THANKS, thank_natex)
df.set_error_successor(State.FINALCOLLEGES, State.END)

#########################################
# Unsure about attending college
#########################################

df.add_system_transition(State.UNSURE_COLLEGE, State.UNSURE_FEELS, '"Why are you unsure?"')

df.add_user_transition(State.UNSURE_FEELS, State.UNSURE_OKAY, '[$emotion=#POS(adj)]')
df.set_error_successor(State.UNSURE_FEELS, State.UNSURE_OKAY_GENERIC)
df.add_system_transition(State.UNSURE_OKAY, State.COMMENT,
                         '[! "It\'s okay to feel " $emotion " Sometimes I feel that way about making decisions too.'
                         'I think if you think about all the pros and cons and get some advice '
                         'from the people around you, you will be able to come to a decision.'
                         'Don\'t worry!"]')
df.add_system_transition(State.UNSURE_OKAY_GENERIC, State.COMMENT,
                         '"That does sound like you have a lot to think about. I am sure you will be able'
                         'to come to a decision soon."')
#########################################
# Error handling and END
#########################################

df.add_system_transition(State.END, State.END, '"It was nice talking with you. Hope you have a nice day."')

df.add_system_transition(State.ERR, State.END, '"Sorry, I\'m not sure I understand that."')
df.add_user_transition(State.END, State.END, yes_natex)
df.set_error_successor(State.END, State.END)

if __name__ == '__main__':
    df.run(debugging=False)
