//need to detect palindrome in a given sequence
//palindrome_o = 1 if a palindorme_o is seen

module palindrome3b(
  input logic clk,
  input logic reset,
  input logic x_i,
  output logic palindrome_o
);
  
  //we will be implementing left shift register and count to count upto 2.
  
  logic [1:0] shift_reg_q;
  logic [1:0] next_shift_reg;
  
  logic [1:0] count_q;
  logic [1:0] next_count;
  
  //implementing flop for storing  current values of shift and count
  always_ff @(posedge clk or posedge reset) begin
    if(reset) begin
      count_q <= 2'b00;
      shift_reg_q <= 2'b00;
    end else begin
      count_q <= next_count;
      shift_reg_q <= next_shift_reg;
    end
  end
  
  //logic for count, count should increment, if 2 is not seen, so that means count msb bit is not set,then count + 1
  assign next_count = count_q[1] ? count_q:count_q+2'b01;
  //logic for shift reg, shift the [0] bit to left and x_i to lsb
  assign next_shift_reg = {shift_reg_q[0], x_i};
  
  //checking palindrome, check the [1] bit with x_i when count's [1] bit is set
  assign palindrome_o = (shift_reg_q[1] == x_i) & count_q[1] ;
  
//   always_comb begin
//     next_count = count_q[1] ? count_q:count_q+2'b01;
//     next_shift_reg = {shift_reg_q[0], x_i};
//     palindrome_o = (shift_reg_q[1] == x_i) & count_q[1] ;
//   end
    
  
endmodule