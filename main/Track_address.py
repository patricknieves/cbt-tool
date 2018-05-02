import Database_manager
import sys


def main(address_to_prove):
    address_to_search = str(address_to_prove)
    print("strart with " + address_to_search)
    Database_manager.initialize_db()
    rels = Database_manager.get_relations(address_to_search)
    while rels:
        curr_addr = rels[0][2]
        print("From: INPUT:" + str(rels[0][1]) + ", OUTPUT " + str(rels[0][2]) + ", HASH: " + str(rels[0][3]))
        rels = Database_manager.get_relations(curr_addr)
    print("finish")

if __name__ == "__main__": main(sys.argv[1])

