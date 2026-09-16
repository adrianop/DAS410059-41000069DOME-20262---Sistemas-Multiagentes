// Contract Net Protocol participant.
//
// Single shared source file: my1st_app.jcm creates m participants from this
// file using "instances: m", so every participantK gets its identity from
// .my_name/1 instead of a per-file belief. Since instances share the same
// initial beliefs, the "differentiated proposal strategies" asked for by
// the assignment come from each proposal drawing its own price at random
// (.random/1), so different instances (and different proposals) end up
// offering different prices.
//
// The price is computed inline in the cfp handler below, not cached in a
// belief set by a separate "+!start" plan: an earlier version compute the
// price once on start-up, but that created a race with incoming cfp
// messages -- a cfp arriving before the (asynchronous) start-up plan had
// finished found no base_price belief yet, so its context failed and the
// message was silently dropped. service/1, unlike base_price/1, is an
// initial belief loaded before the agent's first reasoning cycle, so it is
// always available in time.

+cfp(Task, Service, Initiator)[source(_)]
    : service(Service)
    <- .my_name(Id);
       .random(R);
       Price = 15 + (R * 20);
       .send(Initiator, tell, propose(Task, Price, Id));
       .print("[CNP] ", Id, " proposed ", Price, " for ", Task).

+award(Task, Service, Price, Initiator)[source(_)]
    <- .my_name(Id);
       .print("[CNP] ", Id, " accepted ", Task, " for ", Price);
       .wait(200);
       .send(Initiator, tell, completed(Task, Id)).

+reject(Task)[source(_)]
    <- .my_name(Id);
       .print("[CNP] ", Id, " rejected for ", Task).

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
