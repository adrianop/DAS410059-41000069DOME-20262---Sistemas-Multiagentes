// Contract Net Protocol initiator.
//
// Single shared source file: my1st_app.jcm creates n initiators from this
// file using "instances: n", so every initiatorK gets its identity from
// .my_name/1 instead of a per-file belief. The number of participants (m)
// and of parallel contracts per initiator (i) come from the beliefs
// n_participants/1 and n_contracts/1, set once in the .jcm and shared by
// all instances.
//
// Proposals are only accumulated (+proposal/3), never compared incrementally.
// An earlier version kept a running "best" belief, updated by two plans
// ("no best yet" / "cheaper than current best") triggered on every incoming
// propose. Under i>1 concurrent contracts that pattern is a read-then-write
// race: with two proposals for the same task arriving close together, both
// could be evaluated against the belief base before either's effect was
// applied, so both matched "no best yet" and two best/3 facts ended up
// coexisting -- the one picked by the later query then depended on internal
// belief-base ordering, not on price. Deciding the winner with a single
// .min query, once, after the bidding window closes, has no such window.
//
// TIMING lines (.nano_time) are printed purely for the experiment/report:
// they mark, per task, when the cfp broadcast starts and when the initiator
// has confirmation the winner finished the job, so a total protocol wall
// time can be measured from the log without including JVM/CArtAgO/Moise
// start-up cost.

!start.

+!start
    : n_contracts(I)
    <- .my_name(Id);
       .print("[CNP] ", Id, " starting ", I, " parallel contract(s)");
       for ( .range(K,1,I) ) {
           !!contract(K)
       }.

+!contract(Number)
    : n_participants(M)
    <- .my_name(Id);
       Task = task(Id, Number);
       .nano_time(T0);
       .print("TIMING START ", Task, " ", T0);
       for ( .range(K,1,M) ) {
           .concat("participant",K,P);
           .send(P, tell, cfp(Task, delivery, Id))
       };
       .wait(1000);
       if ( proposal(Task, _, _)
            & .min(Price, proposal(Task,Participant,Price), BestPrice)
            & proposal(Task, Winner, BestPrice) ) {
           for ( .range(K,1,M) ) {
               .concat("participant",K,P);
               .send(P, tell, reject(Task))
           };
           .send(Winner, tell, award(Task, delivery, BestPrice, Id));
           .print("[CNP] ", Id, " awarded ", Task, " to ", Winner, " for ", BestPrice)
       } else {
           .print("[CNP] ", Id, " received no proposals for ", Task)
       };
       .abolish(proposal(Task,_,_)).

+propose(Task, Price, Participant)[source(_)]
    <- +proposal(Task, Participant, Price).

+completed(Task, Participant)[source(_)]
    <- .nano_time(T1);
       .print("TIMING END ", Task, " ", T1);
       .print("[CNP] completed ", Task, " by ", Participant).

{ include("$jacamo/templates/common-cartago.asl") }
{ include("$jacamo/templates/common-moise.asl") }
