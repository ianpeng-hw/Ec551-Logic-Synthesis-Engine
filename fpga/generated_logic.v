module structurallogic(A, B, C, D, E, F, G, out);
    input A, B, C, D, E, F, G;
    output out;
    wire term_0, term_1, term_2;
    and (term_0, B, C, E);
    and (term_1, A, F, G);
    and (term_2, A, C, D);
    or (out, term_0, term_1, term_2);
endmodule
