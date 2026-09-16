// Contract Net Protocol initiator shared by initiator1..initiator3

!start.

+!start
    : initiator(Id)
    <- .print("[CNP] ", Id, " starting 1 parallel contracts");
       !!contract(Id, 1).
//       !!contract(Id, 2);
//       !!contract(Id, 3).

+!contract(Id, Number)
    : initiator(Id)
    <- Task = task(Id, Number);
       .send(participant1, tell, cfp(Task, delivery, Id));
       .send(participant2, tell, cfp(Task, delivery, Id));
       .send(participant3, tell, cfp(Task, delivery, Id));
       .send(participant4, tell, cfp(Task, delivery, Id));
       .wait(1000);
         ?best(Task, Winner, Price);
       .send(participant1, tell, reject(Task));
       .send(participant2, tell, reject(Task));
       .send(participant3, tell, reject(Task));
       .send(participant4, tell, reject(Task));
       .send(Winner, tell, award(Task, delivery, Price, Id));
       .print("[CNP] ", Id, " awarded ", Task, " to ", Winner, " for ", Price);
       -best(Task, Winner, Price).

+propose(Task, Price, Participant)[source(_)]
    : not best(Task, ExistingWinner, ExistingPrice)
    <- +best(Task, Participant, Price).

+propose(Task, Price, Participant)[source(_)]
    : best(Task, Current, CurrentPrice) & Price < CurrentPrice
    <- -best(Task, Current, CurrentPrice);
       +best(Task, Participant, Price).

+completed(Task, Participant)[source(_)]
    <- .print("[CNP] completed ", Task, " by ", Participant).

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
