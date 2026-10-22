module structurallogic(A, B, C, D, E, F, out);
    input A, B, C, D, E, F;
    output out;
    wire not_A, term_0, term_1, term_2;
    not (not_A, A);
    and (term_0, D, E, F);
    and (term_1, B, C);
    and (term_2, not_A, B);
    or (out, term_0, term_1, term_2);
endmodule
