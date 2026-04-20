import json

# Lista proporcionada por el usuario (procesada a mano para el script)
user_data = """
CONGRESISTA	REGIÓN		BANCADA
Aguinaga Recuenco Alejandro Aurelio	Lambayeque	1	FP
Alegría García Luis Arturo 	San Martín	1	FP
Barbarán Reyes Rosangella Andrea	Lima	1	FP
Bustamante Donayre Ernesto	Lima	1	FP
Castillo Rivas Eduardo Enrique 	Piura	1	FP
Chacón Trujillo Nilza Merly	Ancash	1	FP
Flores Ruíz Víctor Seferino	La Libertad	1	FP
Huamán Coronado Raúl	Ica	1	FP
Infantes Castañeda Mery Eliana	Amazonas	1	FP
Jiménez Heredia David Julio	Junín	1	FP
Juárez Gallegos Carmen Patricia	Lima	1	FP
López Morales Jeny Luz	Ucayali	1	FP
Moyano Delgado Martha Lupe	Lima	1	FP
Obando Morgan Auristela Ana	Callao	1	FP
Ramírez García Tania Estefany	Cajamarca	1	FP
Revilla Villanueva César Manuel	Piura	1	FP
Rospigliosi Capurro Fernando Miguel	Lima	1	FP
Santisteban Suclupe Magaly	Tumbes	1	FP
Ventura Angel Héctor José	Tumbes	1	FP
Zeta Chunga Cruz María	Piura	1	FP
Acuña Peralta María Grimaneza	La Libertad	2	APP
Camones Soriano Lady Mercedes	Ancash	2	APP
Chiabra León Roberto Enrique	Lima	2	APP
Cordero Jon Tay Luis Gustavo	Lima Provincias	2	APP
Elías Ávalos José Luis	Ica	2	APP
Flores Ancachi Jorge Luis	Puno	2	APP
García Correa Idelso Manuel	Piura	2	APP
Heidinger Ballesteros Nelcy	Pasco	2	APP
Julon Irigoin Elva Edhit	Cajamarca	2	APP
Kamiche Morante Luis Roberto	La Libertad	2	APP
Lizarzaburu Juan Carlos 	PP.EE.	2	APP
Marticorena Mendoza Jorge Alfonso	Ica	2	APP
Quiroz Barboza Segundo Teodomiro	Cajamarca	2	APP
Ruíz Rodríguez Magaly Rosmery	La Libertad	2	APP
Salhuana Cavides Eduardo	Madre de Dios	2	APP
Soto Reyes Alejandro	Cusco	2	APP
Torres Salinas Rosio	Loreto	2	APP
Arriola Tueros, José Alberto	Lima	3	PP
Bellido Ugarte Guido	Cusco	3	PP
Burgos Oliveros Juan Bartolomé	La Libertad	3	PP
Calle Lobatón Digna	Lima	3	PP
Espinoza Vargas Jhaec Darwin	Ancash	3	PP
Juárez Calle Heidy Lisbeth	Piura	3	PP
Laura Rojas Judith	Lima	3	PP
Luna Gálvez José León	Lima	3	PP
Orue Medina, Ariana Maybee	Callao	3	PP
Paredes Castro Francis Jhasmina	Ucayali	3	PP
Picón Quedo Luis Raúl	Huánuco	3	PP
Tello Montes Nivardo Edgar	Lima	3	PP
Agüero Gutiérrez María Antonieta	Arequipa	4	PL
Balcázar Zelada José María	Lambayeque	4	PL
Cerrón Rojas Waldemar José	Junín	4	PL
Cruz Mamani Flavio	Puno	4	PL
Espíritu Cavero Raúl	San Martin	4	PL
Gonza Castillo Americo	Cajamarca	4	PL
Mita Alanoca Isaac               	Tacna	4	PL
Montalvo Cubas Segundo Toribio	Amazonas	4	PL
Portalatino Ávalos Kelly Roxana	Ancash	4	PL
Reyes Cam Abel Augusto	Huánuco	4	PL
Rivas Chacara Janet Milagros	Lima Provincias	4	PL
Taipe Coronado María Elizabeth	Apurimac	4	PL
Bazán Calderón Diego Alonso Fernando	La Libertad	5	RP
Chirinos Venegas Patricia	Callao	5	RP
Ciccia Vásquez Miguel Angel	Piura	5	RP
Córdova Lobatón María Jessica	Lambayeque	5	RP
Herrera Medina Noelia Rossvith	Callao	5	RP
Jáuregui Martínez María	Lima	5	RP
Medina Minaya Esdras Ricardo	Arequipa	5	RP
Muñante Barrios Alejandro	Lima	5	RP
Trigozo Reátegui Cheryl	San Martín	5	RP
Yarrow Lumbreras Norma Martina	Lima	5	RP
Zeballos Aponte Jorge Arturo	PP.EE.	5	RP
Bermejo Rojas Guillermo	Lima	6	JPP
Coayla Juárez Jorge Samuel	Moquegua	6	JPP
Cutipa Ccama Víctor Raúl	Moquegua	6	JPP
Echevarría Rodríguez Hamlet	Cajamarca	6	JPP
Limachi Quispe Nieves Esmeralda	Tacna	6	JPP
Quispe Mamani Wilson Rusbel	Puno	6	JPP
Sánchez Palomino Roberto Helbert	Lima	6	JPP
Tacuri Valdivia Germán Adolfo	Ayacucho	6	JPP
Ugarte Mamani Jhakeline Katy	Cusco	6	JPP
Varas Meléndez Elías Marcial	Ancash	6	JPP
Azurín Loayza Alfredo	Lima	7	SP
Gutiérrez Ticona Paul Silvio	Apurimac	7	SP
Jeri Oré José Enrique	Lima	7	SP
Medina Hermosilla Elizabeth Sara	Huánuco	7	SP
Morante Figari Jorge Alberto	Loreto	7	SP
Paredes Gonzales Alex Antonio	Arequipa	7	SP
Pazo Nunura José Bernardo	Piura	7	SP
Valer Pinto Héctor	Lima	7	SP
Zea Choquechambi Oscar                   	Puno	7	SP
Zegarra Saboya Ana Zadith 	Loreto	7	SP
Alva Prieto María del Carmen	Lima	8	AP
Alva Rojas Carlos Enrique	La Libertad	8	AP
Aragón Carreño Luis Ángel	Cusco	8	AP
López Ureña Ilich Fredy	Junín	8	AP
Martínez Talavera Pedro Edwin	Arequipa	8	AP
Monteza Facho Silvia María	Cajamarca	8	AP
Mori Celis Juan Carlos	Loreto	8	AP
Portero López Hilda Marleny	Lambayeque	8	AP
Soto Palacios Wilson	Huancavelica	8	AP
Vergara Mendoza Elvis Hernán	Ucayali	8	AP
Amuruz Dulanto Yessica Rosselli	Lima	10	Av.P
Cavero Alva Alejandro Enrique	Lima	10	Av.P
Gonzáles Delgado Diana Carolina	Arequipa	10	Av.P
Paredes Fonseca Karol Ivett	San Martín	10	Av.P
Tudela Gutiérrez Adriana Josefina	Lima	10	Av.P
Williams Zapata José Daniel	Lima	10	Av.P
Dávila Atanacio Pasión Neomias	Pasco	11	BS
Flores Ramírez Alex Randu	Ayacucho	11	BS
Pariona Sinche Alfredo	Huancavelica	11	BS
Quito Sarmiento Bernardo Jaime	Arequipa	11	BS
Robles Araujo Silvana Emperatriz	Junín	11	BS
Acuña Peralta Segundo Héctor	Lambayeque	12	HD
Cueto Aservi José Ernesto	Lima	12	HD
Echaíz Ramos Vda de Nuñez, Gladys Margot	Lima	12	HD
Montoya Manrique Jorge Carlos	Lima	12	HD
Padilla Romero Javier Rommel	Lima Provincias	12	HD
Bazán Narro Sigrid Tesoro	Lima	13	BDP
Luque Ibarra Ruth	Cusco	13	BDP
Paredes Piqué Susel Ana María	Lima	13	BDP
Reymundo Mercado Edgard Cornelio	Junín	13	BDP
Zeballos Madariaga Carlos Javier	Puno	13	BDP
Alcarraz Agüero Yorel Kira  	Lima	14	N.A.
Cortez Aguirre Isabel	Lima	14	N.A.
Doroteo Carbajo Raúl Felipe	Ica	14	N.A.
Málaga Trillo George Edward	Lima	14	N.A.
Olivos Martínez Leslie Vivian	Lima Provincias	14	N.A.
Pablo Medina Flor Aidee	Lima	14	N.A.
Palacios Huáman Margot	Ayacucho	14	N.A.
"""

dni_findings = [
  {"name": "Aguinaga Recuenco Alejandro Aurelio", "dni": "08236035"},
  {"name": "Alegría García Luis Arturo", "dni": "41029272"},
  {"name": "Barbarán Reyes Rosangella Andrea", "dni": "44111357"},
  {"name": "Bustamante Donayre Ernesto", "dni": "08232920"},
  {"name": "Castillo Rivas Eduardo Enrique", "dni": "41620241"},
  {"name": "Infantes Castañeda Mery Eliana", "dni": "01340156"},
  {"name": "Huamán Coronado Raúl", "dni": "21564196"},
  {"name": "Martínez Talavera Pedro Edwin", "dni": "29384343"},
  {"name": "Chacón Trujillo Nilza Merly", "dni": "32402450"},
  {"name": "Flores Ruíz Víctor Seferino", "dni": "17834789"},
  {"name": "Jiménez Heredia David Julio", "dni": "19904257"},
  {"name": "López Morales Jeny Luz", "dni": "32039233"},
  {"name": "Moyano Delgado Martha Lupe", "dni": "07264350"},
  {"name": "Obando Morgan Auristela Ana", "dni": "21434316"},
  {"name": "Cerrón Rojas Waldemar José", "dni": "20036514"},
  {"name": "Ramírez García Tania Estefany", "dni": "43336715"},
  {"name": "Revilla Villanueva César Manuel", "dni": "42168936"},
  {"name": "Ventura Angel Héctor José", "dni": "40585695"},
  {"name": "Zeta Chunga Cruz María", "dni": "02868233"},
  {"name": "Alva Prieto María del Carmen", "dni": "08271323"},
  {"name": "Salhuana Cavides Eduardo", "dni": "24691456"},
  {"name": "Soto Reyes Alejandro", "dni": "23933010"},
  {"name": "Williams Zapata José Daniel", "dni": "07246473"},
  {"name": "Acuña Peralta María Grimaneza", "dni": "17849132"},
  {"name": "Camones Soriano Lady Mercedes", "dni": "32532579"},
  {"name": "Bellido Ugarte Guido", "dni": "23963478"},
  {"name": "Espinoza Vargas Jhaec Darwin", "dni": "41381373"},
  {"name": "Gonzales Delgado Diana Carolina", "dni": "70546213"},
  {"name": "Luna Gálvez José León", "dni": "07246887"},
  {"name": "Tello Montes Nivardo Edgar", "dni": "08253163"},
  {"name": "Calle Lobatón Digna", "dni": "08269558"},
  {"name": "Paredes Castro Francis Jhasmina", "dni": "40858548"},
  {"name": "Alcarraz Agüero Yorel Kira", "dni": "44933973"},
  {"name": "Cortez Aguirre Isabel", "dni": "09210748"},
  {"name": "Doroteo Carbajo Raúl Felipe", "dni": "21406859"},
  {"name": "Málaga Trillo George Edward", "dni": "07834574"},
  {"name": "Reymundo Mercado Edgard Cornelio", "dni": "08266205"},
  {"name": "Zeballos Madariaga Carlos Javier", "dni": "29699661"},
  {"name": "Zeballos Aponte Jorge Arturo", "dni": "09315582"},
  {"name": "Yarrow Lumbreras Norma Martina", "dni": "07218683"},
  {"name": "Chiabra León Roberto Enrique", "dni": "07241281"},
  {"name": "Montoya Manrique Jorge Carlos", "dni": "07241199"},
  {"name": "Padilla Romero Javier Rommel", "dni": "10691398"},
  {"name": "Medina Hermosilla Elizabeth Sara", "dni": "22432857"},
  {"name": "Jeri Oré José Enrique", "dni": "09841804"},
  {"name": "Torres Salinas Rosio", "dni": "05618705"},
  {"name": "Azurín Loayza Alfredo", "dni": "07315151"},
  {"name": "Gutiérrez Ticona Paul Silvio", "dni": "23271165"},
  {"name": "Morante Figari Jorge Alberto", "dni": "05273751"},
  {"name": "Paredes Gonzales Alex Antonio", "dni": "29505856"},
  {"name": "Pazo Nunura José Bernardo", "dni": "02871300"},
  {"name": "Valer Pinto Héctor", "dni": "07519616"},
  {"name": "Zea Choquechambi Oscar", "dni": "01540938"},
  {"name": "Zegarra Saboya Ana Zadith", "dni": "05273578"},
  {"name": "Alva Rojas Carlos Enrique", "dni": "17937985"},
  {"name": "Mori Celis Juan Carlos", "dni": "31023773"},
  {"name": "Monteza Facho Silvia María", "dni": "16667146"},
  {"name": "Aragón Carreño Luis Ángel", "dni": "23953530"},
  {"name": "López Ureña Ilich Fredy", "dni": "41108216"},
  {"name": "Dávila Atanacio Pasión Neomias", "dni": "25700579"},
  {"name": "Paredes Fonseca Karol Ivett", "dni": "41042571"},
  {"name": "Tudela Gutiérrez Adriana Josefina", "dni": "45511383"},
  {"name": "Soto Palacios Wilson", "dni": "43283286"},
  {"name": "Vergara Mendoza Elvis Hernán", "dni": "41703666"},
  {"name": "Amuruz Dulanto Yessica Rosselli", "dni": "40417937"},
  {"name": "Cavero Alva Alejandro Enrique", "dni": "46175510"},
  {"name": "Paredes Piqué Susel Ana María", "dni": "07217351"},
  {"name": "Pablo Medina Flor Aidee", "dni": "09403043"},
  {"name": "Palacios Huáman Margot", "dni": "41444342"},
  {"name": "Bazán Narro Sigrid Tesoro", "dni": "41065184"},
  {"name": "Luque Ibarra Ruth", "dni": "23933069"},
  {"name": "Robles Araujo Silvana Emperatriz", "dni": "43088036"},
  {"name": "Quito Sarmiento Bernardo Jaime", "dni": "29272304"},
  {"name": "Pariona Sinche Alfredo", "dni": "20054714"},
  {"name": "Balcázar Zelada José María", "dni": "16434444"},
  {"name": "Gonza Castillo Americo", "dni": "41187802"},
  {"name": "Taipe Coronado María Elizabeth", "dni": "01150493"},
  {"name": "Echaíz Ramos Gladys", "dni": "06112711"},
  {"name": "Cueto Aservi José Ernesto", "dni": "07241940"}
]

dni_map = {d['name']: d['dni'] for d in dni_findings}

final_list = []
for line in user_data.strip().split("\n"):
    if line.startswith("CONGRESISTA"): continue
    parts = line.split("\t")
    if len(parts) >= 4:
        name = parts[0].strip()
        region = parts[1].strip()
        bench_id = parts[2].strip()
        bench_name = parts[3].strip()
        
        # Intentar match difuso básico o exacto
        dni = dni_map.get(name, "PENDIENTE")
        
        final_list.append({
            "name": name,
            "region": region,
            "bench_id": bench_id,
            "bench_name": bench_name,
            "dni": dni
        })

print(f"Total procesados: {len(final_list)}")
with open("congresistas_dataset.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, indent=2, ensure_ascii=False)
