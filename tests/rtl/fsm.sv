module fsm
#(
    parameter STATES = 4,
    parameter WIDTH = 8
)
(
    input  clk,
    input  rst_n,
    input  [7:0] data_in,
    output [7:0] data_out
);

    reg [7:0] data_out_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_out_reg <= 8'h0;
        end else begin
            data_out_reg <= data_in;
        end
    end

    assign data_out = data_out_reg;

endmodule 