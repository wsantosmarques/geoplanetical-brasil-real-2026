/* Aplicado uma única vez, somente ao bootstrap de campanha nova. */
function BR2026ApplyPeople(sim,createActor) {
 const country=sim.countries.get('076');
 if(!country || country._brRealPeopleVersion)return;
 if(country.pol?.parties?.length!==20 || !country.pol.parties.some(p=>p.id==='PCdoB'))throw new Error('Brasil Real: preset de 20 partidos ausente');
 const roster=BR2026_PEOPLE;
 const byKey=new Map(roster.people.map(p=>[p.key,p]));
 const used=new Set(),ids={},claimed=new Set();
 function bind(record,person){
  if(!person || used.has(person.id))throw new Error('Brasil Real: referência pessoal ausente ou duplicada: '+record.key);
  used.add(person.id);ids[record.key]=person.id;
  const parts=record.name.split(' ');
  Object.assign(person,{name:record.name,given:parts[0],surname:parts.slice(1).join(' '),g:record.g,party:record.party||null,seeded:false,_brRealPersonId:record.key,born:record.birth?.year??null,bornMonth:record.birth?.month!=null?record.birth.month-1:0,background:null,career:[],dynastyId:null,rel:{spouse:null,parents:[],children:[],mentor:null,rivals:[],allies:[]}});
  // Parâmetros neutros de simulação, nunca juízos biográficos.
  for(const key of Object.keys(person.traits||{}))person.traits[key]=key==='authoritarian'?0:0.5;
  const ideology=country.pol.parties.find(p=>p.id===person.party)?.ideology;
  person.ideal=ideology?{...ideology}:{econ:0,social:0,gov:0,nat:0};
  return person;
 }
 for(const record of roster.people.filter(p=>p.bind)){
  const id=record.bind==='president'?(country.leaderId||country.headOfStateId):record.bind==='vice'?country.deputyId:(country.cabinetIds||[]).find(id=>sim.people.get(id)?.office===record.bind);
  bind(record,sim.people.get(id));
 }
 // Reutiliza opositores e figuras existentes, preservando os IDs ligados ao motor.
 const available=[...(country.oppLeaderIds||[]),...Object.values(country.partyBench||{}).flat()];
 const chamberKeys=new Set(roster.parties.map(p=>p.chamberLeaderId));
 for(const record of roster.people.filter(p=>!p.bind).sort((a,b)=>Number(chamberKeys.has(b.key))-Number(chamberKeys.has(a.key)))){
  let person=available.map(id=>sim.people.get(id)).find(p=>p&&p.alive&&!used.has(p.id)&&!claimed.has(p.id)&&p.party===record.party&&['opp_leader','party_figure'].includes(p.role));
  if(!person){const party=country.pol.parties.find(p=>p.id===record.party);person=createActor(sim,country,'party_figure','br-real:'+record.key,record.party,party?.ideology,.0,50,1);}
  claimed.add(person.id);bind(record,person);
 }
 // Remove vínculos fictícios recíprocos e filiação antiga nas reservas partidárias.
 for(const person of sim.people.values())if(!used.has(person.id)){
  for(const [key,value] of Object.entries(person.rel||{})){
   if(Array.isArray(value))person.rel[key]=value.filter(id=>!used.has(id));
   else if(used.has(value))person.rel[key]=null;
  }
 }
 for(const dynasty of sim.dynasties?.values?.()||[])if(Array.isArray(dynasty.memberIds))dynasty.memberIds=dynasty.memberIds.filter(id=>!used.has(id));
 for(const [party,bench] of Object.entries(country.partyBench||{}))country.partyBench[party]=bench.filter(id=>sim.people.get(id)?.party===party);
 for(const [key,id] of Object.entries(ids)){const party=byKey.get(key).party;if(party){const bench=country.partyBench[party]||(country.partyBench[party]=[]);if(!bench.includes(id))bench.push(id);}}
 country._brRealPeopleVersion=roster.version;
 // O próprio objeto pessoa é persistido; o catálogo da UI não redefine cargos no futuro.
 country._brRealPartyPeople=Object.fromEntries(roster.parties.map(p=>[p.partyId,{nationalIds:p.nationalIds.map(k=>ids[k]),chamberLeaderId:ids[p.chamberLeaderId],federationLeaderId:ids[p.federationLeaderId]||null}]));
}
