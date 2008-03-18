// Syntax highlighting test file for System Verilog
// Comments are like this

virtual class Display;
integer v = 'b1010_1011_1100_1101;

 pure virtual task Print();
    $display("v (dec) : ",v);
 endtask

endclass

class HexDisplay extends Display ;

  task Print(); // over-ridden method
    $displayh("v (hex) : ",v);
  endtask

endclass

class OctDisplay extends Display ;

  task Print(); // over-ridden method
    $displayo("v (oct) : ",v);
  endtask

endclass

class BinDisplay extends Display ;

  task Print(); // over-ridden method
    $displayb("v (bin) : ",v);
  endtask

endclass

module poly5;

HexDisplay hx = new();
OctDisplay oc = new();
BinDisplay bn = new();
Display poly;

initial begin
 $display("\n\n");

 poly = hx;
 poly.Print();

 poly = oc;
 poly.Print();

 poly = bn;
 poly.Print();

 $display("\n\n\n");

 $finish;
 end

endmodule
