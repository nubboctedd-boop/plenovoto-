import json
import difflib

# Cargar el dataset consolidado
with open("congresistas_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Resultados del subagente (79 DNIs)
findings = [
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

found_names = [f['name'] for f in findings]

for d in dataset:
    if d['dni'] == 'PENDIENTE':
        # Búsqueda difusa
        matches = difflib.get_close_matches(d['name'], found_names, n=1, cutoff=0.6)
        if matches:
            match_name = matches[0]
            # Encontrar el DNI del match
            for f in findings:
                if f['name'] == match_name:
                    d['dni'] = f['dni']
                    break

# Guardar de nuevo
with open("congresistas_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

# Mostrar restantes
pending = [d['name'] for d in dataset if d['dni'] == 'PENDIENTE']
print(f"Restantes: {len(pending)}")
print("\n".join(pending))
