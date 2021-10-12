from flask import json
from flask.json import load
from flakon import JsonBlueprint
from flask import abort, jsonify, request

from bedrock_a_party.classes.party import CannotPartyAloneError, Party, NotInvitedGuestError, ItemAlreadyInsertedByUser, NotExistingFoodError

parties = JsonBlueprint('parties', __name__)

_LOADED_PARTIES = {}  # dict of available parties
_PARTY_NUMBER = 0  # index of the last created party

#
# These are utility functions. Use them, DON'T CHANGE THEM!!
#

def create_party(req):
    global _LOADED_PARTIES, _PARTY_NUMBER

    # get data from request
    json_data = req.get_json()

    # list of guests
    try:
        guests = json_data['guests']
    except:
        raise CannotPartyAloneError("You cannot party alone!")

    # add party to the loaded parties lists
    _LOADED_PARTIES[str(_PARTY_NUMBER)] = Party(_PARTY_NUMBER, guests)
    _PARTY_NUMBER += 1

    return jsonify({'party_number': _PARTY_NUMBER - 1})


def get_all_parties():
    global _LOADED_PARTIES

    return jsonify(loaded_parties=[party.serialize() for party in _LOADED_PARTIES.values()])


def exists_party(_id):
    global _PARTY_NUMBER
    global _LOADED_PARTIES

    if int(_id) > _PARTY_NUMBER:
        abort(404)  # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(_id in _LOADED_PARTIES):
        abort(410)  # error 410: Gone, i.e. it existed but it's not there anymore


# TODO: complete the decoration
@parties.route("/parties", methods=['GET', 'POST'])
def all_parties():
    if request.method == 'POST':
        try:
            # TODO: create a party
            return create_party(request)

        except CannotPartyAloneError:
            abort(400)
            # TODO: return 400

    elif request.method == 'GET':
        # TODO: get all the parties
        return get_all_parties()


# TODO: complete the decoration
@parties.route("/parties/loaded", methods=['GET'])
def loaded_parties():
    # TODO: returns the number of parties currently loaded in the system
    loaded_parties = 0
    for party in _LOADED_PARTIES:
        loaded_parties += 1
    
    return jsonify({'loaded_parties': loaded_parties})


# TODO: complete the decoration
@parties.route("/party/<id>", methods=['GET', 'DELETE'])
def single_party(id):
    global _LOADED_PARTIES

    # TODO: check if the party is an existing one
    exists_party(id)
    
    if 'GET' == request.method:
        # TODO: retrieve a party
        party = _LOADED_PARTIES[id]
        return jsonify(party.serialize())

    elif 'DELETE' == request.method:
        # TODO: delete a party
        del _LOADED_PARTIES[id]
        
        return jsonify("Party deleted.")

    else:
        return jsonify("Party not found.")
    

# TODO: complete the decoration
@parties.route("/party/<id>/foodlist", methods=['GET'])
def get_foodlist(id):
    global _LOADED_PARTIES

    # TODO: check if the party is an existing one
    exists_party(id)

    if 'GET' == request.method:
        # TODO: retrieve food-list of the party
        party = _LOADED_PARTIES[id]
        return jsonify({'foodlist': party.serialize()['foodlist']})


# TODO: complete the decoration
@parties.route("/party/<id>/foodlist/<user>/<item>", methods=['POST', 'DELETE'])
def edit_foodlist(id, user, item):
    global _LOADED_PARTIES

    # TODO: check if the party is an existing one
    exists_party(id)

    # TODO: retrieve the party
    party = _LOADED_PARTIES[id]
    guests = party.serialize()['guests']

    if 'POST' == request.method:
        # TODO: add item to food-list handling NotInvitedGuestError (401) and ItemAlreadyInsertedByUser (400)      
        #for person in guests:
            #if str(user) == str(person):
                #return jsonify("HERE")
        try:       
            party.add_to_food_list(item, user)                   
            return jsonify((party.serialize())['foodlist'])                
        
        except NotInvitedGuestError:
                    abort(401)

        except ItemAlreadyInsertedByUser:
            abort(400)
       
    if 'DELETE' == request.method:
        # TODO: delete item to food-list handling NotExistingFoodError (400)
        try:
            party.remove_from_food_list(item, user)
            return jsonify({"msg": "Food deleted!"})
            
        except NotExistingFoodError:
            abort(400)
