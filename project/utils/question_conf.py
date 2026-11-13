FTTH_TEMPLATES: list = [
    dict(needs="ONT",
         phrasings=["Which sub-splitter is ONT \"{id}\" connected to?",
                    "What sub-splitter does ONT \"{id}\" attach to?",
                    "Find the sub-splitter serving ONT \"{id}\"."],
         cypher='MATCH (o:ONT {{name: "{id}"}})-[:CONNECTS_TO]->(s:SUB_SPLITTER) RETURN s.name'),

    dict(needs="PORT",
         phrasings=["Which card is port \"{id}\" on?",
                    "What card does port \"{id}\" belong to?"],
         cypher='MATCH (p:PORT {{name: "{id}"}})-[:CONNECTS_TO]->(c:CARD) RETURN c.name'),

    dict(needs="SUB_SPLITTER",
         phrasings=["Which splitter does sub-splitter \"{id}\" feed into?",
                    "What is the parent splitter of sub-splitter \"{id}\"?"],
         cypher='MATCH (s:SUB_SPLITTER {{name: "{id}"}})-[:CONNECTS_TO]->(sp:SPLITTER) RETURN sp.name'),

    dict(needs="ONT",
         phrasings=["Which OLT serves ONT \"{id}\"?",
                    "Trace ONT \"{id}\" back to its OLT.",
                    "What OLT is ONT \"{id}\" ultimately connected to?"],
         cypher='MATCH (o:ONT {{name: "{id}"}})-[:CONNECTS_TO*5..6]->(d:OLT) RETURN d.name'),

    dict(needs="SPLITTER",
         phrasings=["Which OLT does splitter \"{id}\" connect to?",
                    "Find the OLT upstream of splitter \"{id}\"."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})-[:CONNECTS_TO*4]->(d:OLT) RETURN d.name'),

    dict(needs="ONT",
         phrasings=["Which port does ONT \"{id}\" connect through?",
                    "What port is upstream of ONT \"{id}\"?"],
         cypher='MATCH (o:ONT {{name: "{id}"}})-[:CONNECTS_TO*3..4]->(p:PORT) RETURN p.name'),

    dict(needs="SPLITTER",
         phrasings=["Which ONTs are wired directly to splitter \"{id}\", without a sub-splitter?",
                    "List the ONTs attached straight to splitter \"{id}\" with no sub-splitter in between."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO]-(o:ONT) RETURN o.name'),

    dict(needs="SPLITTER",
         phrasings=["Which ONTs reach splitter \"{id}\" through a sub-splitter?",
                    "List the ONTs connected to splitter \"{id}\" via a sub-splitter."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO*2]-(o:ONT) RETURN o.name'),

    dict(needs="SPLITTER",
         phrasings=["Which ONTs are served by splitter \"{id}\", whether directly or through a sub-splitter?",
                    "List every ONT downstream of splitter \"{id}\", either through a sub-splitter or directly."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO*1..2]-(o:ONT) RETURN o.name'),

    dict(needs="SUB_SPLITTER",
         phrasings=["List the ONTs connected to sub-splitter \"{id}\".",
                    "Which ONTs hang off sub-splitter \"{id}\"?"],
         cypher='MATCH (s:SUB_SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO]-(o:ONT) RETURN o.name'),

    dict(needs="OLT",
         phrasings=["How many ONTs does OLT \"{id}\" serve?",
                    "Count the ONTs connected to OLT \"{id}\".",
                    "What is the ONT count for OLT \"{id}\"?"],
         cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO*5..6]-(o:ONT) RETURN count(DISTINCT o) AS total'),

    dict(needs="OLT",
         phrasings=["How many cards does OLT \"{id}\" have?",
                    "Count the cards installed in OLT \"{id}\"."],
         cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO]-(c:CARD) RETURN count(DISTINCT c) AS total'),

    dict(needs="CABIN",
         phrasings=["How many ONTs does cabin \"{id}\" serve?",
                    "Count the ONTs reachable from cabin \"{id}\"."],
         cypher='MATCH (c:CABIN {{name: "{id}"}})-[:CONNECTS_TO]->(sp:SPLITTER) '
                'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) RETURN count(DISTINCT o) AS total'),

    dict(needs="SPLITTER",
         phrasings=["How many sub-splitters does splitter \"{id}\" have?",
                    "Count the sub-splitters under splitter \"{id}\"."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO]-(s:SUB_SPLITTER) '
                'RETURN count(DISTINCT s) AS total'),

    dict(needs=None,
         phrasings=["Which OLTs are made by Huawei?",
                    "List the OLTs from the vendor Huawei."],
         cypher='MATCH (d:OLT {{vendor: "Huawei"}}) RETURN d.name'),

    dict(needs=None,
         phrasings=["Which ports are administratively disabled?",
                    "List the ports whose admin state is disabled."],
         cypher='MATCH (p:PORT {{admin_state: "disabled"}}) RETURN p.name'),

    dict(needs="SPLITTER",
         phrasings=["What is the split ratio of splitter \"{id}\"?",
                    "Give the split ratio of splitter \"{id}\"."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}}) RETURN sp.split_ratio'),

    dict(needs="ONT",
         phrasings=["What is the status of ONT \"{id}\"?",
                    "For ONT \"{id}\", find its status."],
         cypher='MATCH (o:ONT {{name: "{id}"}}) RETURN o.status'),

    dict(needs="ONT",
         phrasings=["Is ONT \"{id}\" currently active?",
                    "Is ONT \"{id}\" in active state?"],
         cypher='MATCH (o:ONT {{name: "{id}"}}) RETURN o.status = "active" AS active',
         alt_cypher='MATCH (o:ONT {{name: "{id}"}}) RETURN o.status'),

    dict(needs="OLT",
         phrasings=["What vendor and model is OLT \"{id}\"?",
                    "Give the vendor and model of OLT \"{id}\"."],
         cypher='MATCH (d:OLT {{name: "{id}"}}) RETURN d.vendor, d.model'),

    dict(needs="OLT",
         phrasings=["Which card is in slot 0 of OLT \"{id}\"?",
                    "What card occupies slot 0 on OLT \"{id}\"?"],
         cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO]-(c:CARD {{slot: 0}}) RETURN c.name'),

    dict(needs="OLT",
         phrasings=["How many faulty ONTs does OLT \"{id}\" serve?",
                    "Count the ONTs in faulty state under OLT \"{id}\"."],
         cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO*5..6]-(o:ONT {{status: "faulty"}}) '
                'RETURN count(DISTINCT o) AS total'),

    dict(needs="SPLITTER",
         phrasings=["Which ONTs on splitter \"{id}\" have a signal weaker than -28 dBm?",
                    "List the ONTs under splitter \"{id}\" with signal below -28 dBm."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO*1..2]-(o:ONT) '
                'WHERE o.signal_dbm < -28 RETURN o.name',
         alt_cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO*1..2]-(o:ONT) '
                    'WHERE o.signal_dbm < -28 RETURN o.name, o.signal_dbm'),

    dict(needs="SPLITTER",
         phrasings=["What is the weakest signal reading among the ONTs served by splitter \"{id}\"?",
                    "Give the lowest signal value of any ONT served by splitter \"{id}\"."],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})<-[:CONNECTS_TO*1..2]-(o:ONT) '
                'RETURN min(o.signal_dbm) AS weakest'),

    dict(needs="SITE",
         phrasings=["Which splitters in SITE {id} were installed before 2020?",
                    "List the splitters in SITE {id} with an install date earlier than 2020."],
         cypher='MATCH (sp:SPLITTER)-[:CONNECTS_TO*4]->(d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                'WHERE sp.install_date < date("2020-01-01") RETURN sp.name'),

    dict(needs="SITE",
         phrasings=["How many faulty ONTs are there in SITE {id}?",
                    "Count the faulty ONTs located in SITE {id}."],
         cypher='MATCH (o:ONT {{status: "faulty"}})-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                'RETURN count(DISTINCT o) AS total'),

    dict(needs="CABIN",
         phrasings=["Which cabin is cabin \"{id}\" the backup for?",
                    "Cabin \"{id}\" acts as backup for which cabin?"],
         cypher='MATCH (c:CABIN {{name: "{id}"}})-[:BACKUP_FOR]->(other:CABIN) RETURN other.name'),

    dict(needs="CABIN",
         phrasings=["Which cabin backs up cabin \"{id}\"?",
                    "Which cabin serves as the standby for cabin \"{id}\"?"],
         cypher='MATCH (c:CABIN)-[:BACKUP_FOR]->(other:CABIN {{name: "{id}"}}) RETURN c.name'),

    dict(needs=None,
         phrasings=["Which cabins have no backup cabin assigned?",
                    "List the cabins that are not backed up by any other cabin."],
         cypher='MATCH (c:CABIN) WHERE NOT EXISTS {{ (:CABIN)-[:BACKUP_FOR]->(c) }} RETURN c.name'),

    dict(needs=None,
         phrasings=["How many cabins act as a backup for another cabin?",
                    "Count the cabins that back up another cabin."],
         cypher='MATCH (c:CABIN)-[:BACKUP_FOR]->(:CABIN) RETURN count(DISTINCT c) AS total'),

    dict(needs="SITE",
         phrasings=["For each OLT in SITE {id}, how many ONTs does it serve?",
                    "Break down the ONT count per OLT in SITE {id}."],
         cypher='MATCH (d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                'MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d) '
                'WITH d, count(DISTINCT o) AS total RETURN d.name, total'),

    dict(needs="CABIN",
         phrasings=["For each splitter on cabin \"{id}\", how many ONTs does it serve?",
                    "Per splitter of cabin \"{id}\", give the ONT count."],
         cypher='MATCH (c:CABIN {{name: "{id}"}})-[:CONNECTS_TO]->(sp:SPLITTER) '
                'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) '
                'WITH sp, count(DISTINCT o) AS total RETURN sp.name, total'),

    dict(needs=None,
         phrasings=["How many OLTs does each vendor supply?",
                    "Break down the OLT count by vendor."],
         cypher='MATCH (d:OLT) WITH d.vendor AS vendor, count(DISTINCT d) AS total '
                'RETURN vendor, total'),

    dict(needs=None,
         phrasings=["Which OLT serves the most ONTs?",
                    "What is the busiest OLT by ONT count?"],
         cypher='MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d:OLT) WITH d, count(DISTINCT o) AS total '
                'RETURN d.name ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d:OLT) WITH d, count(DISTINCT o) AS total '
                    'RETURN d.name, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=["Which site has the most ONTs?",
                    "What site serves the largest number of ONTs?"],
         cypher='MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE) '
                'WITH s, count(DISTINCT o) AS total RETURN s.name ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE) '
                    'WITH s, count(DISTINCT o) AS total RETURN s.name, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=["Which cabin serves the most ONTs?",
                    "What is the largest cabin by ONT count?"],
         cypher='MATCH (c:CABIN)-[:CONNECTS_TO]->(sp:SPLITTER) '
                'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) '
                'WITH c, count(DISTINCT o) AS total RETURN c.name ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (c:CABIN)-[:CONNECTS_TO]->(sp:SPLITTER) '
                    'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) '
                    'WITH c, count(DISTINCT o) AS total RETURN c.name, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=["Which splitter serves the most ONTs?",
                    "What splitter has the highest ONT count?"],
         cypher='MATCH (sp:SPLITTER)<-[:CONNECTS_TO*1..2]-(o:ONT) '
                'WITH sp, count(DISTINCT o) AS total RETURN sp.name ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (sp:SPLITTER)<-[:CONNECTS_TO*1..2]-(o:ONT) '
                    'WITH sp, count(DISTINCT o) AS total RETURN sp.name, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=["Which site has the most faulty ONTs?",
                    "What site has the highest number of ONTs in faulty state?"],
         cypher='MATCH (o:ONT {{status: "faulty"}})-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE) '
                'WITH s, count(DISTINCT o) AS total RETURN s.name ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (o:ONT {{status: "faulty"}})-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE) '
                    'WITH s, count(DISTINCT o) AS total RETURN s.name, total ORDER BY total DESC LIMIT 1'),

    dict(needs="ONT",
         phrasings=["Which site is ONT \"{id}\" in?",
                    "What site does ONT \"{id}\" belong to?",
                    "Locate the site containing ONT \"{id}\"."],
         cypher='MATCH (o:ONT {{name: "{id}"}})-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE) RETURN s.name'),

    dict(needs="SPLITTER",
         phrasings=["Which site is splitter \"{id}\" in?",
                    "What site hosts splitter \"{id}\"?"],
         cypher='MATCH (sp:SPLITTER {{name: "{id}"}})-[:CONNECTS_TO*4]->(d:OLT)-[:IN_SITE]->(s:SITE) RETURN s.name'),

    dict(needs="SITE",
         phrasings=["How many ONTs are there in SITE {id}?",
                    "Count all ONTs located in SITE {id}."],
         cypher='MATCH (o:ONT)-[:CONNECTS_TO*5..6]->(d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                'RETURN count(DISTINCT o) AS total'),

    dict(needs=None,
         phrasings=["Which sub-splitters have no ONTs connected?",
                    "List sub-splitters with zero ONTs."],
         cypher='MATCH (s:SUB_SPLITTER) WHERE NOT EXISTS {{ (s)<-[:CONNECTS_TO]-(:ONT) }} RETURN s.name'),

    dict(needs=None,
         phrasings=["Which splitters are not connected to any cabin?",
                    "Find splitters with no cabin."],
         cypher='MATCH (sp:SPLITTER) WHERE NOT EXISTS {{ (sp)<-[:CONNECTS_TO]-(:CABIN) }} RETURN sp.name'),

    dict(needs=None,
         phrasings=["What are the cards with no ports?",
                    "List cards that have no ports attached."],
         cypher='MATCH (c:CARD) WHERE NOT EXISTS {{ (c)<-[:CONNECTS_TO]-(:PORT) }} RETURN c.name'),

    dict(needs="SITE",
         phrasings=["Which splitters in SITE {id} serve more than 40 ONTs?",
                    "In SITE {id}, find splitters with over 40 ONTs."],
         cypher='MATCH (sp:SPLITTER)-[:CONNECTS_TO*4]->(d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) '
                'WITH sp, count(DISTINCT o) AS total WHERE total > 40 RETURN sp.name, total',
         alt_cypher='MATCH (sp:SPLITTER)-[:CONNECTS_TO*4]->(d:OLT)-[:IN_SITE]->(s:SITE {{name: "{id}"}}) '
                    'MATCH (o:ONT)-[:CONNECTS_TO*1..2]->(sp) '
                    'WITH sp, count(DISTINCT o) AS total WHERE total > 40 RETURN sp.name'),

    dict(needs="OLT",
         phrasings=["Which cards on OLT \"{id}\" have more than 4 ports?",
                    "On OLT \"{id}\", list cards with over 4 ports."],
         cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO]-(c:CARD) '
                'MATCH (p:PORT)-[:CONNECTS_TO]->(c) '
                'WITH c, count(DISTINCT p) AS total WHERE total > 4 RETURN c.name, total',
         alt_cypher='MATCH (d:OLT {{name: "{id}"}})<-[:CONNECTS_TO]-(c:CARD) '
                    'MATCH (p:PORT)-[:CONNECTS_TO]->(c) '
                    'WITH c, count(DISTINCT p) AS total WHERE total > 4 RETURN c.name'),

    dict(needs=None,
         phrasings=["Which 32-way splitters serve more than 60 ONTs?",
                    "Find splitters with a split ratio of 32 that carry over 60 ONTs."],
         cypher='MATCH (sp:SPLITTER {{split_ratio: 32}})<-[:CONNECTS_TO*1..2]-(o:ONT) '
                'WITH sp, count(DISTINCT o) AS total WHERE total > 60 RETURN sp.name, total',
         alt_cypher='MATCH (sp:SPLITTER {{split_ratio: 32}})<-[:CONNECTS_TO*1..2]-(o:ONT) '
                    'WITH sp, count(DISTINCT o) AS total WHERE total > 60 RETURN sp.name'),

    dict(needs="ONT", cypher=None,
         phrasings=["What is the bandwidth of ONT \"{id}\"?",
                    "How much throughput does ONT \"{id}\" have?"]),

    dict(needs="ONT", cypher=None,
         phrasings=["Which router serves ONT \"{id}\"?",
                    "Find the firewall protecting ONT \"{id}\"."]),

    dict(needs="ONT", cypher=None,
         phrasings=["Who is the customer on ONT \"{id}\"?",
                    "What is the subscriber name for ONT \"{id}\"?"]),

    dict(needs="OLT", cypher=None,
         phrasings=["What is the operating temperature of OLT \"{id}\"?",
                    "How much power does OLT \"{id}\" draw?"]),

    dict(needs="SPLITTER", cypher=None,
         phrasings=["Which technician installed splitter \"{id}\"?",
                    "What was the purchase cost of splitter \"{id}\"?"]),
]

HOSPITAL_TEMPLATES: list = [
    dict(needs="Appointment",
         phrasings=['Which patient is appointment "{id}" for?',
                    'Give the patient id for appointment "{id}".'],
         cypher='MATCH (a:Appointment {{appoIntmentId: {id}}})-[:FOR_PATIENT]->(p:Patient) '
                'RETURN p.patientId',
         alt_cypher='MATCH (a:Appointment {{appoIntmentId: {id}}})-[:FOR_PATIENT]->(p:Patient) '
                    'RETURN p.fName, p.lName'),

    dict(needs="Appointment",
         phrasings=['Which doctor is appointment "{id}" with?',
                    'Give the doctor id for appointment "{id}".'],
         cypher='MATCH (a:Appointment {{appoIntmentId: {id}}})-[:WITH_DOCTOR]->(d:Doctor) '
                'RETURN d.doctId',
         alt_cypher='MATCH (a:Appointment {{appoIntmentId: {id}}})-[:WITH_DOCTOR]->(d:Doctor) '
                    'RETURN d.fName, d.lName'),

    dict(needs="Bed",
         phrasings=['Which ward is bed "{id}" in?',
                    'What ward does bed "{id}" belong to?'],
         cypher='MATCH (b:Bed {{bedNo: {id}}})-[:IN_WARD]->(w:Ward) RETURN w.wardName'),

    dict(needs="Room",
         phrasings=['Which department is room "{id}" in?',
                    'What department does room "{id}" belong to?'],
         cypher='MATCH (r:Room {{roomNo: {id}}})-[:IN_DEPARTMENT]->(dep:Department) '
                'RETURN dep.deptName'),

    dict(needs="Doctor",
         phrasings=['Which department does doctor "{id}" belong to?',
                    'What is the department of doctor "{id}"?'],
         cypher='MATCH (d:Doctor {{doctId: {id}}})-[:BELONGS_TO]->(dep:Department) '
                'RETURN dep.deptName'),

    dict(needs="MedicalRecord",
         phrasings=['What diagnosis and treatment are recorded in medical record "{id}"?',
                    'Give the diagnosis and treatment on medical record "{id}".'],
         cypher='MATCH (m:MedicalRecord {{recordId: {id}}}) RETURN m.diagnosis, m.treatment'),

    dict(needs="RoomRecord",
         phrasings=['Which room was assigned on room record "{id}"?',
                    'Give the room number for room record "{id}".'],
         cypher='MATCH (rr:RoomRecord {{admissonId: {id}}})-[:ASSIGNED_ROOM]->(r:Room) '
                'RETURN r.roomNo'),

    dict(needs="BedRecord",
         phrasings=['Which bed was assigned on bed record "{id}"?',
                    'Give the bed number for bed record "{id}".'],
         cypher='MATCH (br:BedRecord {{admissionId: {id}}})-[:ASSIGNED_BED]->(b:Bed) '
                'RETURN b.bedNo'),

    dict(needs="Nurse",
         phrasings=['What is the contact number of nurse "{id}"?',
                    'Give the phone number recorded for nurse "{id}".'],
         cypher='MATCH (n:Nurse {{nurseId: {id}}}) RETURN n.conatctNo'),

    dict(needs="Patient",
         phrasings=['Which doctors has patient "{id}" had appointments with? Give their ids.',
                    'List the ids of doctors who have appointments with patient "{id}".'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (a)-[:WITH_DOCTOR]->(d:Doctor) RETURN DISTINCT d.doctId'),

    dict(needs="Doctor",
         phrasings=['Which patients have appointments with doctor "{id}"? Give their ids.',
                    'List the ids of patients booked with doctor "{id}".'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor {{doctId: {id}}}) '
                'MATCH (a)-[:FOR_PATIENT]->(p:Patient) RETURN DISTINCT p.patientId'),

    dict(needs="Patient",
         phrasings=['Which doctors wrote medical records for patient "{id}"? Give their ids.',
                    'List the ids of doctors who authored medical records for patient "{id}".'],
         cypher='MATCH (m:MedicalRecord)-[:OF_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (m)-[:WRITTEN_BY]->(d:Doctor) RETURN DISTINCT d.doctId'),

    dict(needs="Patient",
         phrasings=['Which wards has patient "{id}" occupied a bed in?',
                    'List the wards where patient "{id}" was assigned a bed.'],
         cypher='MATCH (br:BedRecord)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (br)-[:ASSIGNED_BED]->(b:Bed)-[:IN_WARD]->(w:Ward) '
                'RETURN DISTINCT w.wardName'),

    dict(needs="Doctor",
         phrasings=['Which nurses assisted surgeries performed by doctor "{id}"? Give their ids.',
                    'List the ids of nurses who assisted in surgeries by doctor "{id}".'],
         cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor {{doctId: {id}}}) '
                'MATCH (s)-[:ASSISTED_BY_NURSE]->(n:Nurse) RETURN DISTINCT n.nurseId'),

    dict(needs="Patient",
         phrasings=['In which rooms did patient "{id}" have surgery?',
                    'List the room numbers where patient "{id}" was operated on.'],
         cypher='MATCH (s:SurgeryRecord)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (s)-[:IN_ROOM]->(r:Room) RETURN DISTINCT r.roomNo'),

    dict(needs="Bed",
         phrasings=['Which department is bed "{id}" ultimately in?',
                    'Trace bed "{id}" through its ward to a department.'],
         cypher='MATCH (b:Bed {{bedNo: {id}}})-[:IN_WARD]->(w:Ward)-[:IN_DEPARTMENT]->(dep:Department) '
                'RETURN dep.deptName'),

    dict(needs="Patient",
         phrasings=['Which departments has patient "{id}" been seen in through appointments?',
                    'List the departments of the doctors patient "{id}" had appointments with.'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (a)-[:WITH_DOCTOR]->(d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                'RETURN DISTINCT dep.deptName'),

    dict(needs="Patient",
         phrasings=['Which departments did patient "{id}" stay in, going by their room records?',
                    'List the departments of the rooms assigned to patient "{id}".'],
         cypher='MATCH (rr:RoomRecord)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'MATCH (rr)-[:ASSIGNED_ROOM]->(r:Room)-[:IN_DEPARTMENT]->(dep:Department) '
                'RETURN DISTINCT dep.deptName'),

    dict(needs="SurgeryRecord",
         phrasings=['Which department was surgery "{id}" carried out in?',
                    'Give the department of the room used for surgery "{id}".'],
         cypher='MATCH (s:SurgeryRecord {{surgeryId: {id}}})-[:IN_ROOM]->(r:Room)'
                '-[:IN_DEPARTMENT]->(dep:Department) RETURN dep.deptName'),

    dict(needs="Patient",
         phrasings=['How many appointments does patient "{id}" have?',
                    'Count the appointments booked for patient "{id}".'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'RETURN count(DISTINCT a) AS total'),

    dict(needs="Doctor",
         phrasings=['How many appointments does doctor "{id}" have?',
                    'Count the appointments assigned to doctor "{id}".'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor {{doctId: {id}}}) '
                'RETURN count(DISTINCT a) AS total'),

    dict(needs="Doctor",
         phrasings=['How many surgeries has doctor "{id}" performed?',
                    'Count the surgery records for doctor "{id}".'],
         cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor {{doctId: {id}}}) '
                'RETURN count(DISTINCT s) AS total'),

    dict(needs=("Department", "deptName"),
         phrasings=['How many doctors work in {id}?',
                    'Count the doctors belonging to {id}.'],
         cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                'RETURN count(DISTINCT d) AS total'),

    dict(needs=("Ward", "wardName"),
         phrasings=['How many beds are in the "{id}"?',
                    'Count the beds belonging to the "{id}".'],
         cypher='MATCH (b:Bed)-[:IN_WARD]->(w:Ward {{wardName: "{id}"}}) '
                'RETURN count(DISTINCT b) AS total'),

    dict(needs="Patient",
         phrasings=['What is the total amount patient "{id}" paid across all appointments?',
                    'Sum the payment amounts on appointments for patient "{id}".'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'RETURN sum(a.paymentAmount) AS total'),

    dict(needs="Doctor",
         phrasings=['How many completed appointments does doctor "{id}" have?',
                    'Count the appointments with doctor "{id}" whose status is Completed.'],
         cypher='MATCH (a:Appointment {{appointmentStatus: "Completed"}})'
                '-[:WITH_DOCTOR]->(d:Doctor {{doctId: {id}}}) '
                'RETURN count(DISTINCT a) AS total'),

    dict(needs="Patient",
         phrasings=['How many appointments of patient "{id}" were cancelled?',
                    'Count the cancelled appointments for patient "{id}".'],
         cypher='MATCH (a:Appointment {{appointmentStatus: "Cancelled"}})'
                '-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) '
                'RETURN count(DISTINCT a) AS total'),

    dict(needs=("Department", "deptName"),
         phrasings=['How many female doctors are in {id}?',
                    'Count the doctors in {id} whose gender is F.'],
         cypher='MATCH (d:Doctor {{gender: "F"}})-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                'RETURN count(DISTINCT d) AS total'),

    dict(needs=("Appointment", "reason"),
         phrasings=['How many appointments were booked for {id}?',
                    'Count the appointments whose reason is {id}.'],
         cypher='MATCH (a:Appointment {{reason: "{id}"}}) RETURN count(DISTINCT a) AS total'),

    dict(needs=("Department", "deptName"),
         phrasings=['What is the total payment collected on appointments in {id}?',
                    'Sum the appointment payments for doctors belonging to {id}.'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)'
                '-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                'RETURN sum(a.paymentAmount) AS total'),

    dict(needs="Patient",
         phrasings=['Which of patient "{id}"\'s appointments were paid by Insurance? Give their ids.',
                    'List the appointment ids for patient "{id}" with Insurance as the payment mode.'],
         cypher='MATCH (a:Appointment {{modeOfPayment: "Insurance"}})'
                '-[:FOR_PATIENT]->(p:Patient {{patientId: {id}}}) RETURN a.appoIntmentId'),

    dict(needs=None,
         phrasings=['Which appointments were no-shows? Give their ids.',
                    'List the ids of appointments whose status is No-Show.'],
         cypher='MATCH (a:Appointment {{appointmentStatus: "No-Show"}}) RETURN a.appoIntmentId'),

    dict(needs=None,
         phrasings=['How many appointments were held online?',
                    'Count the appointments whose mode is Online.'],
         cypher='MATCH (a:Appointment {{modeOfAppointment: "Online"}}) '
                'RETURN count(DISTINCT a) AS total'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which medical records have no next visit scheduled? Give their ids.',
                    'List the ids of medical records where nextVisit is null.'],
         cypher='MATCH (m:MedicalRecord) WHERE m.nextVisit IS NULL RETURN m.recordId'),

    dict(needs=None,
         phrasings=['How many appointments are there of each status?',
                    'Break down the appointment count by status.'],
         cypher='MATCH (a:Appointment) WITH a.appointmentStatus AS status, '
                'count(DISTINCT a) AS total RETURN status, total'),

    dict(needs=None,
         phrasings=['How much was paid through each payment mode on appointments?',
                    'Break down total appointment payments by mode of payment.'],
         cypher='MATCH (a:Appointment) WITH a.modeOfPayment AS mode, '
                'sum(a.paymentAmount) AS total RETURN mode, total'),

    dict(needs=None,
         phrasings=['How many doctors belong to each department?',
                    'Break down the doctor count by department.'],
         cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                'WITH dep.deptName AS department, count(DISTINCT d) AS total '
                'RETURN department, total'),

    dict(needs=None,
         phrasings=['How many beds does each ward have?',
                    'Break down the bed count by ward.'],
         cypher='MATCH (b:Bed)-[:IN_WARD]->(w:Ward) '
                'WITH w.wardName AS ward, count(DISTINCT b) AS total RETURN ward, total'),

    dict(needs=("Department", "deptName"),
         phrasings=['For each doctor in {id}, how many appointments do they have?',
                    'Per doctor in {id}, give the appointment count.'],
         cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                'MATCH (a:Appointment)-[:WITH_DOCTOR]->(d) '
                'WITH d, count(DISTINCT a) AS total RETURN d.doctId, total'),

    dict(needs=None,
         phrasings=['Which doctor has the most appointments? Give their id.',
                    'Which doctor id appears on the highest number of appointments?'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor) '
                'WITH d, count(DISTINCT a) AS total RETURN d.doctId ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor) '
                    'WITH d, count(DISTINCT a) AS total RETURN d.doctId, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which department has the most doctors?',
                    'What department employs the largest number of doctors?'],
         cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                'WITH dep, count(DISTINCT d) AS total RETURN dep.deptName '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                    'WITH dep, count(DISTINCT d) AS total RETURN dep.deptName, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which patient has the most appointments? Give their id.',
                    'Which patient id appears on the highest number of appointments?'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient) '
                'WITH p, count(DISTINCT a) AS total RETURN p.patientId ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient) '
                    'WITH p, count(DISTINCT a) AS total RETURN p.patientId, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which doctor has performed the most surgeries? Give their id.',
                    'Which doctor id appears on the most surgery records?'],
         cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor) '
                'WITH d, count(DISTINCT s) AS total RETURN d.doctId ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor) '
                    'WITH d, count(DISTINCT s) AS total RETURN d.doctId, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which department collected the most in appointment payments?',
                    'What department has the highest total appointment revenue?'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                'WITH dep, sum(a.paymentAmount) AS total RETURN dep.deptName '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                    'WITH dep, sum(a.paymentAmount) AS total RETURN dep.deptName, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which ward has the most beds?',
                    'What ward contains the largest number of beds?'],
         cypher='MATCH (b:Bed)-[:IN_WARD]->(w:Ward) WITH w, count(DISTINCT b) AS total '
                'RETURN w.wardName ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (b:Bed)-[:IN_WARD]->(w:Ward) WITH w, count(DISTINCT b) AS total '
                    'RETURN w.wardName, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which patients have no appointments at all? Give their ids.',
                    'List the ids of patients with no appointment booked.'],
         cypher='MATCH (p:Patient) WHERE NOT EXISTS {{ (:Appointment)-[:FOR_PATIENT]->(p) }} '
                'RETURN p.patientId'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which doctors have never performed a surgery? Give their ids.',
                    'List the ids of doctors with no surgery records.'],
         cypher='MATCH (d:Doctor) WHERE NOT EXISTS {{ (:SurgeryRecord)-[:PERFORMED_BY]->(d) }} '
                'RETURN d.doctId'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which nurses have never assisted a surgery? Give their ids.',
                    'List the ids of nurses with no surgery assistance recorded.'],
         cypher='MATCH (n:Nurse) WHERE NOT EXISTS {{ (:SurgeryRecord)-[:ASSISTED_BY_NURSE]->(n) }} '
                'RETURN n.nurseId'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which rooms have never been used for surgery?',
                    'List the room numbers with no surgery record attached.'],
         cypher='MATCH (r:Room) WHERE NOT EXISTS {{ (:SurgeryRecord)-[:IN_ROOM]->(r) }} '
                'RETURN r.roomNo'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which doctors have appointments but no staff shift assigned? Give their ids.',
                    'List the ids of doctors who appear on an appointment but on no staff shift.'],
         cypher='MATCH (a:Appointment)-[:WITH_DOCTOR]->(d:Doctor) '
                'WHERE NOT EXISTS {{ (:StaffShift)-[:ASSIGNED_DOCTOR]->(d) }} '
                'RETURN DISTINCT d.doctId'),

    dict(needs=None,
         phrasings=['Which patients have had both a surgery and a bed record? Give their ids.',
                    'List the ids of patients appearing on both a surgery record and a bed record.'],
         cypher='MATCH (s:SurgeryRecord)-[:FOR_PATIENT]->(p:Patient) '
                'MATCH (br:BedRecord)-[:FOR_PATIENT]->(p) RETURN DISTINCT p.patientId'),

    dict(needs=None,
         phrasings=['Which patients have both a room record and an appointment? Give their ids.',
                    'List the ids of patients who appear on a room record and on an appointment.'],
         cypher='MATCH (rr:RoomRecord)-[:FOR_PATIENT]->(p:Patient) '
                'MATCH (a:Appointment)-[:FOR_PATIENT]->(p) RETURN DISTINCT p.patientId'),

    dict(needs=None,
         phrasings=['Which doctors have both performed a surgery and written a medical record? Give their ids.',
                    'List the ids of doctors appearing on both a surgery record and a medical record.'],
         cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor) '
                'MATCH (m:MedicalRecord)-[:WRITTEN_BY]->(d) RETURN DISTINCT d.doctId'),

    dict(needs=None,
         phrasings=['Which nurses have been assigned to both a bed record and a room record? Give their ids.',
                    'List the ids of nurses appearing on both a bed record and a room record.'],
         cypher='MATCH (br:BedRecord)-[:ASSIGNED_NURSE]->(n:Nurse) '
                'MATCH (rr:RoomRecord)-[:ASSIGNED_NURSE]->(n) RETURN DISTINCT n.nurseId'),

    dict(needs=None,
         phrasings=['Which helpers both assisted a surgery and were assigned to a bed record? Give their ids.',
                    'List the ids of helpers appearing on both a surgery record and a bed record.'],
         cypher='MATCH (s:SurgeryRecord)-[:ASSISTED_BY_HELPER]->(h:Helper) '
                'MATCH (br:BedRecord)-[:ASSIGNED_HELPER]->(h) RETURN DISTINCT h.helperId'),

    dict(needs=None,
         phrasings=[
             'Which nurses have both assisted a surgery and been assigned to a bed record for the same patient? Give their ids.',
             'List the ids of nurses appearing on a surgery record and a bed record for the same patient.'],
         cypher='MATCH (s:SurgeryRecord)-[:FOR_PATIENT]->(p:Patient) '
                'MATCH (s)-[:ASSISTED_BY_NURSE]->(n:Nurse) '
                'MATCH (br:BedRecord)-[:FOR_PATIENT]->(p) '
                'MATCH (br)-[:ASSIGNED_NURSE]->(n) RETURN DISTINCT n.nurseId'),

    dict(needs=None,
         phrasings=['Which patients have been treated by doctors from more than one department? Give their ids.',
                    'List the ids of patients whose appointment doctors span at least two departments.'],
         cypher='MATCH (a:Appointment)-[:FOR_PATIENT]->(p:Patient) '
                'MATCH (a)-[:WITH_DOCTOR]->(d:Doctor)-[:BELONGS_TO]->(dep:Department) '
                'WITH p, count(DISTINCT dep) AS departments WHERE departments > 1 '
                'RETURN p.patientId'),

    dict(needs=None,
         phrasings=[
             'Which nurses work in a different department from the doctor whose surgeries they assist? Give the nurse ids.',
             'List the ids of nurses assisting a surgery where the operating doctor belongs to another department.'],
         cypher='MATCH (s:SurgeryRecord)-[:ASSISTED_BY_NURSE]->(n:Nurse)-[:BELONGS_TO]->(nd:Department) '
                'MATCH (s)-[:PERFORMED_BY]->(d:Doctor)-[:BELONGS_TO]->(dd:Department) '
                'WHERE nd <> dd RETURN DISTINCT n.nurseId'),

    dict(needs=("Department", "deptName"),
         phrasings=['Which doctors in {id} have more than 1 appointment? Give their ids.',
                    'In {id}, list the ids of doctors with over 1 appointment.'],
         cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                'MATCH (a:Appointment)-[:WITH_DOCTOR]->(d) '
                'WITH d, count(DISTINCT a) AS total WHERE total > 1 RETURN d.doctId, total',
         alt_cypher='MATCH (d:Doctor)-[:BELONGS_TO]->(dep:Department {{deptName: "{id}"}}) '
                    'MATCH (a:Appointment)-[:WITH_DOCTOR]->(d) '
                    'WITH d, count(DISTINCT a) AS total WHERE total > 1 RETURN d.doctId'),

    dict(needs=None,
         phrasings=['Which patients have more than 2 completed appointments? Give their ids.',
                    'List the ids of patients with over 2 appointments in Completed status.'],
         cypher='MATCH (a:Appointment {{appointmentStatus: "Completed"}})-[:FOR_PATIENT]->(p:Patient) '
                'WITH p, count(DISTINCT a) AS total WHERE total > 2 RETURN p.patientId, total',
         alt_cypher='MATCH (a:Appointment {{appointmentStatus: "Completed"}})-[:FOR_PATIENT]->(p:Patient) '
                    'WITH p, count(DISTINCT a) AS total WHERE total > 2 RETURN p.patientId'),

    dict(needs=None,
         phrasings=['Which female doctors have performed at least one surgery? Give their ids.',
                    'List the ids of doctors whose gender is F and who appear on a surgery record.'],
         cypher='MATCH (s:SurgeryRecord)-[:PERFORMED_BY]->(d:Doctor {{gender: "F"}}) '
                'RETURN DISTINCT d.doctId'),

    dict(needs="Patient", cypher=None,
         phrasings=['What is the insurance policy number of patient "{id}"?',
                    'Which insurance provider covers patient "{id}"?']),

    dict(needs="Doctor", cypher=None,
         phrasings=['What is the salary of doctor "{id}"?',
                    'How many years of experience does doctor "{id}" have?']),

    dict(needs="Patient", cypher=None,
         phrasings=['What is the email address of patient "{id}"?',
                    'What is the blood type of patient "{id}"?']),

    dict(needs="MedicalRecord", cypher=None,
         phrasings=['What dosage was prescribed in medical record "{id}"?',
                    'Which pharmacy filled the prescription for medical record "{id}"?']),

    dict(needs="Room", cypher=None,
         phrasings=['What floor is room "{id}" on?',
                    'How much does room "{id}" cost per night?']),

    dict(needs=None, cypher=None,
         phrasings=['How many of them are there?',
                    'Who was on duty that day?']),
]

ECOMMERCE_TEMPLATES: list = [
    dict(needs="Transaction",
         phrasings=['Which customer placed transaction "{id}"?',
                    'Give the customer id on transaction "{id}".'],
         cypher='MATCH (t:Transaction {{transactionId: "{id}"}})-[:PLACED_BY]->(c:Customer) '
                'RETURN c.customerId',
         alt_cypher='MATCH (t:Transaction {{transactionId: "{id}"}})-[:PLACED_BY]->(c:Customer) '
                    'RETURN c.firstName, c.lastName'),

    dict(needs="Transaction",
         phrasings=['Which product is in transaction "{id}"?',
                    'Give the product id contained in transaction "{id}".'],
         cypher='MATCH (t:Transaction {{transactionId: "{id}"}})-[:CONTAINS_PRODUCT]->(p:Product) '
                'RETURN p.productId',
         alt_cypher='MATCH (t:Transaction {{transactionId: "{id}"}})-[:CONTAINS_PRODUCT]->(p:Product) '
                    'RETURN p.name'),

    dict(needs="Transaction",
         phrasings=['What is the status and revenue of transaction "{id}"?',
                    'Give the status and revenue recorded on transaction "{id}".'],
         cypher='MATCH (t:Transaction {{transactionId: "{id}"}}) RETURN t.status, t.revenueUsd'),

    dict(needs="Return",
         phrasings=['Which customer made return "{id}"?',
                    'Give the customer id on return "{id}".'],
         cypher='MATCH (r:Return {{returnId: "{id}"}})-[:BY_CUSTOMER]->(c:Customer) '
                'RETURN c.customerId',
         alt_cypher='MATCH (r:Return {{returnId: "{id}"}})-[:FOR_TRANSACTION]->(:Transaction)'
                    '-[:PLACED_BY]->(c:Customer) RETURN c.customerId'),

    dict(needs="Product",
         phrasings=['What brand and category is product "{id}"?',
                    'Give the brand and category of product "{id}".'],
         cypher='MATCH (p:Product {{productId: "{id}"}}) RETURN p.brand, p.category'),

    dict(needs="Product",
         phrasings=['Which warehouses stock product "{id}", and how many units does each hold?',
                    'For product "{id}", give each warehouse and its stock level.'],
         cypher='MATCH (w:Warehouse)-[s:STOCKS]->(p:Product {{productId: "{id}"}}) '
                'RETURN w.warehouseLocation, s.stockUnits'),

    dict(needs="Product",
         phrasings=['How many units of product "{id}" are in stock across all warehouses?',
                    'Give the total stock of product "{id}" over every warehouse.'],
         cypher='MATCH (:Warehouse)-[s:STOCKS]->(p:Product {{productId: "{id}"}}) '
                'RETURN sum(s.stockUnits) AS total'),

    dict(needs="Product",
         phrasings=['Who is the primary supplier of product "{id}"?',
                    'Give the supplier marked as primary for product "{id}".'],
         cypher='MATCH (s:Supplier)-[sup:SUPPLIES]->(p:Product {{productId: "{id}"}}) '
                'WHERE sup.isPrimary = true RETURN s.supplierName'),

    dict(needs="Product",
         phrasings=['What unit cost does each supplier charge for product "{id}"?',
                    'For product "{id}", give each supplier and its unit cost.'],
         cypher='MATCH (s:Supplier)-[sup:SUPPLIES]->(p:Product {{productId: "{id}"}}) '
                'RETURN s.supplierName, sup.unitCostUsd'),

    dict(needs="Warehouse",
         phrasings=['Which product is lowest in stock at {id}?',
                    'Give the product with the fewest units held at {id}.'],
         cypher='MATCH (w:Warehouse {{warehouseLocation: "{id}"}})-[s:STOCKS]->(p:Product) '
                'RETURN p.productId ORDER BY s.stockUnits ASC LIMIT 1',
         alt_cypher='MATCH (w:Warehouse {{warehouseLocation: "{id}"}})-[s:STOCKS]->(p:Product) '
                    'RETURN p.productId, s.stockUnits ORDER BY s.stockUnits ASC LIMIT 1'),

    dict(needs="Product",
         phrasings=['When was product "{id}" last restocked, and where?',
                    'Give the warehouse and last restock date for product "{id}".'],
         cypher='MATCH (w:Warehouse)-[s:STOCKS]->(p:Product {{productId: "{id}"}}) '
                'RETURN w.warehouseLocation, s.lastRestockDate '
                'ORDER BY s.lastRestockDate DESC LIMIT 1'),

    dict(needs="Supplier",
         phrasings=['How many products does {id} supply as the primary supplier?',
                    'Count the products where {id} is marked primary.'],
         cypher='MATCH (s:Supplier {{supplierName: "{id}"}})-[sup:SUPPLIES]->(p:Product) '
                'WHERE sup.isPrimary = true RETURN count(DISTINCT p) AS total'),

    dict(needs="Customer",
         phrasings=['Which products has customer "{id}" bought? Give their ids.',
                    'List the product ids appearing on transactions of customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'MATCH (t)-[:CONTAINS_PRODUCT]->(p:Product) RETURN DISTINCT p.productId'),

    dict(needs="Customer",
         phrasings=['Which products has customer "{id}" returned? Give their ids.',
                    'List the product ids on returns made by customer "{id}".'],
         cypher='MATCH (r:Return)-[:BY_CUSTOMER]->(c:Customer {{customerId: "{id}"}}) '
                'MATCH (r)-[:OF_PRODUCT]->(p:Product) RETURN DISTINCT p.productId'),

    dict(needs="Product",
         phrasings=['How many different customers have bought product "{id}"?',
                    'Count the distinct customers who bought product "{id}".'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product {{productId: "{id}"}}) '
                'MATCH (t)-[:PLACED_BY]->(c:Customer) RETURN count(DISTINCT c) AS total'),

    dict(needs="Supplier",
         phrasings=['Which product categories does {id} supply?',
                    'List the categories of the products supplied by {id}.'],
         cypher='MATCH (s:Supplier {{supplierName: "{id}"}})-[:SUPPLIES]->(p:Product) '
                'RETURN DISTINCT p.category'),

    dict(needs="Customer",
         phrasings=['Which suppliers made the products customer "{id}" bought? Give their names.',
                    'List the suppliers of every product on transactions of customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'MATCH (t)-[:CONTAINS_PRODUCT]->(p:Product) '
                'MATCH (s:Supplier)-[:SUPPLIES]->(p) RETURN DISTINCT s.supplierName'),

    dict(needs="Customer",
         phrasings=['How many transactions does customer "{id}" have?',
                    'Count the transactions placed by customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'RETURN count(DISTINCT t) AS total'),

    dict(needs="Product",
         phrasings=['How many times has product "{id}" been returned?',
                    'Count the returns of product "{id}".'],
         cypher='MATCH (r:Return)-[:OF_PRODUCT]->(p:Product {{productId: "{id}"}}) '
                'RETURN count(DISTINCT r) AS total'),

    dict(needs="Customer",
         phrasings=['What is the total revenue from customer "{id}"?',
                    'Sum the revenue across all transactions of customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'RETURN sum(t.revenueUsd) AS total'),

    dict(needs="Product",
         phrasings=['What is the total profit made on product "{id}"?',
                    'Sum the profit over every transaction containing product "{id}".'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product {{productId: "{id}"}}) '
                'RETURN sum(t.profitUsd) AS total'),

    dict(needs="Customer",
         phrasings=['How much has been refunded to customer "{id}" in total?',
                    'Sum the refund amounts on returns by customer "{id}".'],
         cypher='MATCH (r:Return)-[:BY_CUSTOMER]->(c:Customer {{customerId: "{id}"}}) '
                'RETURN sum(r.refundAmountUsd) AS total'),

    dict(needs="Product",
         phrasings=['How many units of product "{id}" have been sold in total?',
                    'Sum the quantity across every transaction containing product "{id}".'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product {{productId: "{id}"}}) '
                'RETURN sum(t.quantity) AS total'),

    dict(needs=("Product", "category"),
         phrasings=['What is the highest unit price in the {id} category?',
                    'Give the most expensive unit price among {id} products.'],
         cypher='MATCH (p:Product {{category: "{id}"}}) RETURN max(p.unitPriceUsd) AS highest'),

    dict(needs=None,
         phrasings=['How many customers are premium members?',
                    'Count the customers flagged as premium.'],
         cypher='MATCH (c:Customer) WHERE c.isPremium = true '
                'RETURN count(DISTINCT c) AS total'),

    dict(needs=None,
         phrasings=['Which products are no longer active? Give their ids.',
                    'List the ids of products whose active flag is false.'],
         cypher='MATCH (p:Product) WHERE p.isActive = false RETURN p.productId'),

    dict(needs=None,
         phrasings=['How many returns were not restocked?',
                    'Count the returns whose restocked flag is false.'],
         cypher='MATCH (r:Return) WHERE r.restocked = false '
                'RETURN count(DISTINCT r) AS total'),

    dict(needs="Customer",
         phrasings=['When was the most recent transaction by customer "{id}"?',
                    'Give the date of the latest transaction placed by customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'RETURN max(t.date) AS latest'),

    dict(needs="Customer",
         phrasings=['How much revenue did customer "{id}" generate in 2024?',
                    'Sum the 2024 transaction revenue for customer "{id}".'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{customerId: "{id}"}}) '
                'WHERE t.date.year = 2024 RETURN sum(t.revenueUsd) AS total'),

    dict(needs=None,
         phrasings=['How many transactions were there in 2023?',
                    'Count the transactions dated in 2023.'],
         cypher='MATCH (t:Transaction) WHERE t.date.year = 2023 '
                'RETURN count(DISTINCT t) AS total'),

    dict(needs=None,
         phrasings=['How much revenue was there in each year?',
                    'Break down total transaction revenue by year.'],
         cypher='MATCH (t:Transaction) WITH t.date.year AS year, sum(t.revenueUsd) AS total '
                'RETURN year, total'),

    dict(needs=("Product", "category"),
         phrasings=['Which {id} product was launched most recently? Give its id.',
                    'Give the id of the newest product in the {id} category by launch date.'],
         cypher='MATCH (p:Product {{category: "{id}"}}) '
                'RETURN p.productId ORDER BY p.launchDate DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['How much revenue did each product category bring in?',
                    'Break down total revenue by product category.'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product) '
                'WITH p.category AS category, sum(t.revenueUsd) AS total '
                'RETURN category, total'),

    dict(needs=None,
         phrasings=['How many transactions are there of each status?',
                    'Break down the transaction count by status.'],
         cypher='MATCH (t:Transaction) WITH t.status AS status, count(DISTINCT t) AS total '
                'RETURN status, total'),

    dict(needs=None,
         phrasings=['How many returns were there for each reason?',
                    'Break down the return count by reason.'],
         cypher='MATCH (r:Return) WITH r.reason AS reason, count(DISTINCT r) AS total '
                'RETURN reason, total'),

    dict(needs=None,
         phrasings=['For each category, how many different customers have bought from it?',
                    'Per product category, count the distinct customers who bought one.'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product) '
                'MATCH (t)-[:PLACED_BY]->(c:Customer) '
                'WITH p.category AS category, count(DISTINCT c) AS total '
                'RETURN category, total'),

    dict(needs="Supplier",
         phrasings=['For each product {id} supplies, what is the lead time?',
                    'Per product supplied by {id}, give the lead time in days.'],
         cypher='MATCH (s:Supplier {{supplierName: "{id}"}})-[sup:SUPPLIES]->(p:Product) '
                'RETURN p.productId, sup.leadTimeDays'),

    dict(needs=None,
         phrasings=['Which customer has spent the most in total? Give their id.',
                    'Which customer id has the highest total revenue?'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer) '
                'WITH c, sum(t.revenueUsd) AS total RETURN c.customerId '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer) '
                    'WITH c, sum(t.revenueUsd) AS total RETURN c.customerId, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which product has been returned the most? Give its id.',
                    'Which product id appears on the highest number of returns?'],
         cypher='MATCH (r:Return)-[:OF_PRODUCT]->(p:Product) '
                'WITH p, count(DISTINCT r) AS total RETURN p.productId '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (r:Return)-[:OF_PRODUCT]->(p:Product) '
                    'WITH p, count(DISTINCT r) AS total RETURN p.productId, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which category brought in the most revenue?',
                    'What product category has the highest total revenue?'],
         cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product) '
                'WITH p.category AS category, sum(t.revenueUsd) AS total '
                'RETURN category ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p:Product) '
                    'WITH p.category AS category, sum(t.revenueUsd) AS total '
                    'RETURN category, total ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which supplier supplies the most products?',
                    'What supplier covers the largest number of products?'],
         cypher='MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) '
                'WITH s, count(DISTINCT p) AS total RETURN s.supplierName '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) '
                    'WITH s, count(DISTINCT p) AS total RETURN s.supplierName, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None,
         phrasings=['Which warehouse holds the most units overall?',
                    'What warehouse has the highest total stock?'],
         cypher='MATCH (w:Warehouse)-[s:STOCKS]->(:Product) '
                'WITH w, sum(s.stockUnits) AS total RETURN w.warehouseLocation '
                'ORDER BY total DESC LIMIT 1',
         alt_cypher='MATCH (w:Warehouse)-[s:STOCKS]->(:Product) '
                    'WITH w, sum(s.stockUnits) AS total RETURN w.warehouseLocation, total '
                    'ORDER BY total DESC LIMIT 1'),

    dict(needs=None, allow_empty=True,
         phrasings=['Which products have never been sold? Give their ids.',
                    'List the ids of products that appear on no transaction.'],
         cypher='MATCH (p:Product) WHERE NOT EXISTS {{ (:Transaction)-[:CONTAINS_PRODUCT]->(p) }} '
                'RETURN p.productId'),

    dict(needs="Product",
         phrasings=['Which suppliers do not supply product "{id}"? Give their names.',
                    'List the suppliers that have no supply arrangement for product "{id}".'],
         cypher='MATCH (s:Supplier) '
                'WHERE NOT EXISTS {{ (s)-[:SUPPLIES]->(:Product {{productId: "{id}"}}) }} '
                'RETURN s.supplierName'),

    dict(needs="Product",
         phrasings=['Which warehouses do not stock product "{id}"?',
                    'List the warehouses holding no units of product "{id}".'],
         cypher='MATCH (w:Warehouse) '
                'WHERE NOT EXISTS {{ (w)-[:STOCKS]->(:Product {{productId: "{id}"}}) }} '
                'RETURN w.warehouseLocation'),

    dict(needs=None,
         phrasings=['How many customers have never returned anything?',
                    'Count the customers with no returns.'],
         cypher='MATCH (c:Customer) WHERE NOT EXISTS {{ (:Return)-[:BY_CUSTOMER]->(c) }} '
                'RETURN count(DISTINCT c) AS total'),

    dict(needs=None,
         phrasings=['How many customers have bought and also returned the same product?',
                    'Count the customers who returned a product they had bought.'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer) '
                'MATCH (t)-[:CONTAINS_PRODUCT]->(p:Product) '
                'MATCH (r:Return)-[:BY_CUSTOMER]->(c) '
                'MATCH (r)-[:OF_PRODUCT]->(p) RETURN count(DISTINCT c) AS total'),

    dict(needs=None,
         phrasings=['How many products come from more than one supplier?',
                    'Count the products supplied by at least two suppliers.'],
         cypher='MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) '
                'WITH p, count(DISTINCT s) AS suppliers WHERE suppliers > 1 '
                'RETURN count(DISTINCT p) AS total'),

    dict(needs=None,
         phrasings=['How many products are stocked below the minimum order quantity their supplier sets?',
                    'Count the products whose warehouse stock is under the supplier minimum order quantity.'],
         cypher='MATCH (w:Warehouse)-[st:STOCKS]->(p:Product) '
                'MATCH (:Supplier)-[sp:SUPPLIES]->(p) '
                'WHERE st.stockUnits < sp.minOrderQty RETURN count(DISTINCT p) AS total'),

    dict(needs=None,
         phrasings=['Which suppliers are the primary supplier of a discontinued product? Give their names.',
                    'List the suppliers marked primary on a product that is no longer active.'],
         cypher='MATCH (s:Supplier)-[sup:SUPPLIES]->(p:Product) '
                'WHERE sup.isPrimary = true AND p.isActive = false '
                'RETURN DISTINCT s.supplierName'),

    dict(needs=None,
         phrasings=['How many customers bought the product with the longest primary-supplier lead time?',
                    'Count the customers who bought the product whose primary supplier is slowest.'],
         cypher='MATCH (:Supplier)-[sup:SUPPLIES]->(p:Product) WHERE sup.isPrimary = true '
                'WITH p ORDER BY sup.leadTimeDays DESC LIMIT 1 '
                'MATCH (t:Transaction)-[:CONTAINS_PRODUCT]->(p) '
                'MATCH (t)-[:PLACED_BY]->(c:Customer) RETURN count(DISTINCT c) AS total'),

    dict(needs=None,
         phrasings=['How many transactions were discounted by more than 20%?',
                    'Count the transactions whose discount is above 0.2.'],
         cypher='MATCH (t:Transaction) WHERE t.discountPct > 0.2 '
                'RETURN count(DISTINCT t) AS total'),

    dict(needs=("Transaction", "status"),
         phrasings=['What is the average discount on {id} transactions?',
                    'Give the mean discount percentage across transactions in {id} status.'],
         cypher='MATCH (t:Transaction {{status: "{id}"}}) '
                'RETURN avg(t.discountPct) AS average'),

    dict(needs=("Return", "reason"),
         phrasings=['How many returns for {id} were not restocked?',
                    'Count the returns with reason {id} that were not put back in stock.'],
         cypher='MATCH (r:Return {{reason: "{id}"}}) WHERE r.restocked = false '
                'RETURN count(DISTINCT r) AS total'),

    dict(needs=("Customer", "country"),
         phrasings=['What is the total revenue from customers in {id}?',
                    'Sum the transaction revenue for customers whose country is {id}.'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer {{country: "{id}"}}) '
                'RETURN sum(t.revenueUsd) AS total'),

    dict(needs=None,
         phrasings=['How many premium customers have more than one transaction?',
                    'Count the premium customers with at least two transactions.'],
         cypher='MATCH (t:Transaction)-[:PLACED_BY]->(c:Customer) WHERE c.isPremium = true '
                'WITH c, count(DISTINCT t) AS total WHERE total > 1 '
                'RETURN count(DISTINCT c) AS customers'),

    dict(needs=("Product", "brand"),
         phrasings=['How many units of {id} products are in stock across all warehouses?',
                    'Sum the stock units held for products of the brand {id}.'],
         cypher='MATCH (:Warehouse)-[s:STOCKS]->(p:Product {{brand: "{id}"}}) '
                'RETURN sum(s.stockUnits) AS total'),

    dict(needs="Customer", cypher=None,
         phrasings=['What is the shipping address of customer "{id}"?',
                    'What phone number is on file for customer "{id}"?']),

    dict(needs="Product", cypher=None,
         phrasings=['What is the average review rating of product "{id}"?',
                    'How many stars has product "{id}" been given?']),

    dict(needs="Supplier", cypher=None,
         phrasings=['What country is {id} based in?',
                    'What is the contact email for {id}?']),

    dict(needs="Transaction", cypher=None,
         phrasings=['Which employee processed transaction "{id}"?',
                    'What courier delivered transaction "{id}"?']),

    dict(needs=None, cypher=None,
         phrasings=['How many of them are left?',
                    'What did they order last time?']),
]

HOSPITAL_ID_PROP = {
    "Appointment": "appoIntmentId",
    "Bed": "bedNo",
    "BedRecord": "admissionId",
    "Department": "deptId",
    "Doctor": "doctId",
    "Helper": "helperId",
    "MedicalRecord": "recordId",
    "Nurse": "nurseId",
    "Patient": "patientId",
    "Room": "roomNo",
    "RoomRecord": "admissonId",
    "StaffShift": "shiftId",
    "SurgeryRecord": "surgeryId",
    "Ward": "wardNo",
}

ECOMMERCE_ID_PROP = {
    "Customer": "customerId",
    "Product": "productId",
    "Return": "returnId",
    "Supplier": "supplierName",
    "Transaction": "transactionId",
    "Warehouse": "warehouseLocation",
}


def get_templates(dataset: str) -> list:
    match dataset:
        case "ftth":
            return FTTH_TEMPLATES
        case "hospital":
            return HOSPITAL_TEMPLATES
        case "ecommerce":
            return ECOMMERCE_TEMPLATES
        case _:
            raise Exception(f"Dataset not supported")


def get_per_template(dataset: str) -> int:
    match dataset:
        case "ftth" | "ecommerce":
            return 5
        case "hospital":
            return 4
        case _:
            raise Exception(f"Dataset not supported")


def get_id_prop(dataset: str, label: str) -> str:
    match dataset:
        case "ftth":
            return "name"
        case "hospital":
            return HOSPITAL_ID_PROP.get(label, "name")
        case "ecommerce":
            return ECOMMERCE_ID_PROP.get(label, "name")
        case _:
            raise Exception(f"Dataset not supported")
