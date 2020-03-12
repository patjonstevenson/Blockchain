# Paste your version of blockchain.py from the client_mining_p
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):
        """
        Adds a new transaction to the list of transactions
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1


    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # Append the block to the chain
        self.chain.append(block)

        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # Create the block_string
        string_block = json.dumps(block, sort_keys=True)

        # Hash this string using sha256
        raw_hash = hashlib.sha256(string_block.encode())
        
        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand
        hex_hash = raw_hash.hexdigest()
        
        # Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """
        # TODO
        block_string = json.dumps(block, sort_keys=True)

        # Search for proof through brute force
        proof = 0
        while self.valid_proof(block_string, proof) is False:
            proof += 1
        
        return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        # return True or False
        return guess_hash[:6] == "000000"
        


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def receive_transaction():
    # TODO: Handle non json request
    values = request.get_json()
    # breakpoint()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        response = {'message': 'Missing values'}
        return jsonify(response), 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block index {index}'}
    return jsonify(response), 201

@app.route('/mine', methods=['POST']) 
def mine():
    # Run the proof of work algorithm to get the next proof
    # proof = blockchain.proof_of_work(blockchain.last_block)

    # Forge the new Block by adding it to the chain with the proof
    # previous_hash = blockchain.hash(blockchain.last_block)
    # block = blockchain.new_block(proof, previous_hash)

    try:
        data = request.get_json()
    except ValueError:
        print("Error:  Non-json response")
        print("Response returned:")
        print(data)
        return
    required = ['proof', 'id']

    # Brian's way of doing it. I kind of like it more.
    if not all(k in data for k in required):
        return jsonify({'message': "ERROR: Proof and ID required"}), 400 

    # if not data['proof'] or not data['id']:
    #     return jsonify({'message': "ERROR: Proof and ID required"}), 400

    last_block = blockchain.last_block
    block_string = json.dumps(last_block, sort_keys=True)

    is_valid = blockchain.valid_proof(block_string, data['proof'])

    if is_valid:
        blockchain.new_transaction('0', data['id'], 1)

        last_hash = blockchain.hash(last_block)
        blockchain.new_block(data['proof'], last_hash)

        response = {
            # TODO: Send a JSON response with the new block
            'message': 'New Block Forged'
        }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'block': blockchain.last_block
    }
    return jsonify(response), 200

@app.route('/validate', methods=['POST'])
def validate_proof(request):
    block_string, proof = request
    
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    
    # Return True or False
    return guess_hash[:3] == "000"


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
