"""Test script to check why address is being flagged as blacklisted."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.database import FirestoreDB

# Test addresses
addr1 = "1fz29bqp82pe3vxxcszomnq3kshfmzfme3"  # Should be in database
addr2 = "1fz29bqp82pe3vxxcszomnq3kshfmzfme6"  # Should NOT be in database

db = FirestoreDB()

print("=" * 80)
print("Testing Address Check")
print("=" * 80)

print(f"\nAddress 1: {addr1}")
print(f"Address 2: {addr2}")
print(f"\nAre they the same? {addr1 == addr2}")
print(f"Address 1 lower: {addr1.lower()}")
print(f"Address 2 lower: {addr2.lower()}")

print("\n" + "=" * 80)
print("Checking Address 1 (should be found):")
print("=" * 80)
label1 = db.get_address_label(addr1)
if label1:
    print(f"✅ Found: {label1.address} on chain {label1.chain}, label: {label1.label}")
    print(f"   Program: {label1.program}")
    print(f"   Source: {label1.source}")
else:
    print("❌ Not found in database")

print("\n" + "=" * 80)
print("Checking Address 2 (should NOT be found):")
print("=" * 80)
label2 = db.get_address_label(addr2)
if label2:
    print(f"⚠️  FOUND (FALSE POSITIVE!): {label2.address} on chain {label2.chain}, label: {label2.label}")
    print(f"   Program: {label2.program}")
    print(f"   Source: {label2.source}")
    print(f"   This is a BUG - address should not be found!")
else:
    print("✅ Correctly not found in database")

print("\n" + "=" * 80)
print("Checking all labels for Address 2:")
print("=" * 80)
all_labels2 = db.get_all_address_labels(addr2)
if all_labels2:
    print(f"⚠️  Found {len(all_labels2)} label(s):")
    for label in all_labels2:
        print(f"   - {label.address} on {label.chain}, label: {label.label}")
else:
    print("✅ No labels found (correct)")

print("\n" + "=" * 80)
print("Direct Firestore Query Test:")
print("=" * 80)
if db.connected:
    # Direct query
    query = db.db.collection('address_labels').where('address', '==', addr2.lower())
    docs = list(query.stream())
    print(f"Direct query returned {len(docs)} document(s)")
    for doc in docs:
        data = doc.to_dict()
        print(f"   Document ID: {doc.id}")
        print(f"   Address: {data.get('address')}")
        print(f"   Chain: {data.get('chain')}")
        print(f"   Label: {data.get('label')}")
        print(f"   Full data: {data}")

