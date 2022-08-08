from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,sig):
    
    print("Check if signature is valid")
    
    payload_text = json.dumps(payload)
    
    if payload['platform'] == 'Ethereum':

        # Check Ethereum
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_text)

        if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
            g.session.add(new_order)
            g.session.commit()
            return jsonify( True )
        else:
            log_message(payload_text)
            return jsonify( False )
    else:
        # Check Algorand
        if algosdk.util.verify_bytes(payload_text.encode('utf-8'),sig,pk):
            g.session.add(new_order)
            g.session.commit()
            return jsonify( True )                      
        else:
            log_message(payload_text)
            return jsonify( False )

def fill_order(order,txes=[]):
    
    for existing_order in txes:
        
        # Check if currencies match
        if existing_order.buy_currency == new_order.sell_currency and existing_order.sell_currency == new_order.buy_currency:

            # Check if exchange rates match
            if existing_order.sell_amount * new_order.sell_amount >= new_order.buy_amount * existing_order.buy_amount:
                
                #If a match is found between order and existing_order do the trade
                existing_order.filled = datetime.now()
                new_order.filled = datetime.now()
                existing_order.counterparty_id = new_order.id
                new_order.counterparty_id = existing_order.id
                session.commit()
                break
                    
    if existing_order.buy_amount > new_order.sell_amount:
        #create order

        buy_amount = existing_order.buy_amount - new_order.sell_amount
        sell_amount = existing_order.sell_amount / existing_order.buy_amount * buy_amount

        child_data = {'buy_currency': existing_order.buy_currency,
                       'sell_currency': existing_order.sell_currency,
                       'buy_amount': buy_amount,
                       'sell_amount': sell_amount,
                       'sender_pk': existing_order.sender_pk,
                       'receiver_pk': existing_order.receiver_pk,
                       'creator_id': existing_order.id
                      }
        
        child_order = Order(**{f:child_data[f] for f in fields_child})
        session.add(child_order)
        session.commit()

    elif new_order.buy_amount > existing_order.sell_amount:
        #create order

        buy_amount = new_order.buy_amount - existing_order.sell_amount
        sell_amount = new_order.sell_amount / new_order.buy_amount * buy_amount

        child_data = {'buy_currency': new_order.buy_currency,
                       'sell_currency': new_order.sell_currency,
                       'buy_amount': buy_amount,
                       'sell_amount': sell_amount,
                       'sender_pk': new_order.sender_pk,
                       'receiver_pk': new_order.receiver_pk,
                       'creator_id': new_order.id
                      }
        
        child_order = Order(**{f:child_data[f] for f in fields_child})
        session.add(child_order)
        session.commit()
  
def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    with open('server_log.txt', 'a') as log_file:
        log_file.write(json.dumps(d))

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session
        
        payload = content.get("payload")
        sig = content['sig']
        pk = payload.get("sender_pk")
        
        # Create order
        
        order_data = {'sender_pk': payload.get("sender_pk"),
                      'receiver_pk': payload.get("receiver_pk"),
                      'buy_currency': payload.get("buy_currency"),
                      'sell_currency': payload.get("sell_currency"),
                      'buy_amount': payload.get("buy_amount"),
                      'sell_amount': payload.get("sell_amount"),
                      'signature': sig}
        
        new_order_fields = ['sender_pk','receiver_pk','buy_currency','sell_currency','buy_amount','sell_amount','signature']
        new_order = Order(**{f:order_data[f] for f in new_order_fields})

        print("Begin process")
        
        # TODO: Check the signature

        print(check_sig(payload,sig))
        
        # TODO: Add the order to the database
        
        # TODO: Fill the order
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
