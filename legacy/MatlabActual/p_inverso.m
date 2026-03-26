% problema inverso
% mantiene la oerientacion actual
ux=T5(1,1); uy=T5(2,1); uz=T5(3,1);
vx=T5(1,2); vy=T5(2,2); vz=T5(3,2);
wx=T5(1,3); wy=T5(2,3); wz=T5(3,3);
% ingresa nueva posicion del efector
newpos=input('inserta nueva posicion(0:No/1:Si):');
if newpos==0,
    qx=T5(1,4); qy=T5(2,4); qz=T5(3,4);
elseif newpos==1,
    qx=input('inserta nueva px(400-607):');
    qy=input('inserta nueva py(400-607):');
    qz=input('inserta nueva pz( 20-947):');
end    
% Calculo del theta1
theta1=atan(qy/qx);
%Calculo del theta5
inter=ux*sin(theta1)-uy*cos(theta1);
if (inter > 1)
    inter=1;
end
if (inter < -1)
    inter=-1;
end
theta5=asin(inter);
%Calculo del theta3
theta234=atan2((-uz/cos(theta5)),((ux*cos(theta1)+uy*sin(theta1))/cos(theta5)));
k1=qx*cos(theta1)+qy*sin(theta1)-a1+d5*sin(theta234);
k2=-qz+d1-d5*cos(theta234);
inter=(k1^2+k2^2-a2^2-a3^2)/(2*a2*a3);
if (inter > 1)
    inter=1;
end
if (inter < -1)
    inter=-1;
end
theta3=acos(inter);
% Calculo de theta2
cost2=(k1*(a2+a3*cos(theta3))+k2*a3*sin(theta3))/(a2^2+a3^2+2*a2*a3*cos(theta3));
sint2=(-k1*a3*sin(theta3)+k2*(a2+a3*cos(theta3)))/(a2^2+a3^2+2*a2*a3*cos(theta3));
theta2=atan2(sint2,cost2);
% Calculo de theta4
theta4=theta234-theta2-theta3;

t1=theta1*180/pi
t2=theta2*180/pi
t3=theta3*180/pi
t4=theta4*180/pi
t5=theta5*180/pi

% Grafica usando problema directo
% base % dibuja la base del manipulador
% 
% % matriz del hombro respecto a base
% alpha1=-pi/2;
% d1		= 340;
% a1		= l1;
% A1=[ cos(theta1)  -cos(alpha1)*sin(theta1)	  	sin(alpha1)*sin(theta1) 	a1*cos(theta1);
%      sin(theta1)   cos(alpha1)*cos(theta1)     -sin(alpha1)*cos(theta1) 	a1*sin(theta1);
% 	      0		          sin(alpha1)	                cos(alpha1)    		d1;
% 	      0		              0	                          0		         1		];
% shoulder(A1)
% if sw == 1,
%    st=sendmov(1,round(t1/0.094),'Com1')
% end    
% % Matriz del codo respecto a hombro
% alpha2= 0;
% d2		= 0;
% a2		= l2;
% A2=[ cos(theta2)  -cos(alpha2)*sin(theta2)	  	sin(alpha2)*sin(theta2) 	a2*cos(theta2);
%      sin(theta2)   cos(alpha2)*cos(theta2)     -sin(alpha2)*cos(theta2) 	a2*sin(theta2);
% 	     0		          sin(alpha2)	                cos(alpha2)    		d2;
%    	  0		              0	                          0		         1		];
% Link1(A1*A2)       
% if sw == 1,
%    st=sendmov(2,round(t2/0.1175),'Com1')
% end 
% % Matriz muñeca respecto al codo
% alpha3= 0;
% d3		= 0;
% a3		= l2;
% A3=[ cos(theta3)  -cos(alpha3)*sin(theta3)	  	sin(alpha3)*sin(theta3) 	a3*cos(theta3);
%      sin(theta3)   cos(alpha3)*cos(theta3)     -sin(alpha3)*cos(theta3) 	a3*sin(theta3);
% 	     0		          sin(alpha3)	                cos(alpha3)    		d3;
%    	  0		              0	                          0		         1		];
% Link2(A1*A2*A3)
% if sw == 1,
%    st=sendmov(3,round(-(t2+t3)/0.1175),'Com1')
% end 
% 
% % Matriz Muñeca (pitch)
%  alpha4=  -pi/2;
%  d4		= 0;
%  a4		= 0;
%  A4=[ cos(theta4)  -cos(alpha4)*sin(theta4)	  	sin(alpha4)*sin(theta4) 	a4*cos(theta4);
%       sin(theta4)   cos(alpha4)*cos(theta4)     -sin(alpha4)*cos(theta4) 	a4*sin(theta4);
% 	     0		          sin(alpha4)	                cos(alpha4)    		d4;
%    	  0		              0	                          0		         1		];
% if sw == 1,
%    st=sendm45(round((t4)/0.458),round((-t4)/0.458) ,'Com1')
% end 
% 
% % Matriz Muñeca (roll) a Gripper
% alpha5=0;     
% d5		= 151;
% a5		= 0;
% A5=[ cos(theta5)  -cos(alpha5)*sin(theta5)	  	sin(alpha5)*sin(theta5) 	a5*cos(theta5);
%     sin(theta5)   cos(alpha5)*cos(theta5)     -sin(alpha5)*cos(theta5) 	   a5*sin(theta5);
% 	     0		          sin(alpha5)	                cos(alpha5)    		d5;
%    	  0		              0	                          0		         1		];
% if sw == 1,
%    st=sendm45(round(-t5/0.458),round(-t5/0.458) ,'Com1')
% end 
% 
% Gripper(A1*A2*A3*A4*A5,op)     
%      
% % Calculo de vector de posicion. 
% T5=A1*A2*A3*A4*A5;
% T4=A1*A2*A3*A4;
% T3=A1*A2*A3;
% T2=A1*A2;
% T1=A1;
% 
%  x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
%  y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
%  z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];
%  
%  view([112.5,30])
%  plot3(x,y,z),
%  grid on
