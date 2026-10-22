module structurallogic(A, B, C, F);
    input A, B, C;
    output F;
    wire not_A, term_0, term_1;
    not (not_A, A);
    and (term_0, not_A, B);
    and (term_1, A, C);
    or (F, term_0, term_1);
endmodule
