module structurallogic(A, B, C, D, E, G, F);
    input A, B, C, D, E, G;
    output F;
    wire term_0, term_1, term_2;
    and (term_0, E, G);
    and (term_1, C, D);
    and (term_2, A, B);
    or (F, term_0, term_1, term_2);
endmodule
