// Contract Net Protocol participant shared by participant1..participant4

+cfp(Task, Service, Initiator)[source(_)]
    : participant(Id) & service(Service) & base_price(Base)
    <- Price = Base;
       .send(Initiator, tell, propose(Task, Price, Id));
       .print("[CNP] ", Id, " proposed ", Price, " for ", Task).

+award(Task, Service, Price, Initiator)[source(_)]
    : participant(Id)
    <- .print("[CNP] ", Id, " accepted ", Task, " for ", Price);
       .wait(200);
       .send(Initiator, tell, completed(Task, Id)).

+reject(Task)[source(_)]
    : participant(Id)
    <- .print("[CNP] ", Id, " rejected for ", Task).

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
