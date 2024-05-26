function varargout = GpEntrenarNormal(varargin)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%INICIALIZAR%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    % GPENTRENARNORMAL M-file for GpEntrenarNormal.fig
    %      GPENTRENARNORMAL, by itself, creates a new GPENTRENARNORMAL or raises the existing
    %      singleton*.
    %
    %      H = GPENTRENARNORMAL returns the handle to a new GPENTRENARNORMAL or the handle to
    %      the existing singleton*.
    %
    %      GPENTRENARNORMAL('CALLBACK',hObject,eventData,handles,...) calls the local
    %      function named CALLBACK in GPENTRENARNORMAL.M with the given input arguments.
    %
    %      GPENTRENARNORMAL('Property','Value',...) creates a new GPENTRENARNORMAL or raises the
    %      existing singleton*.  Starting from the left, property value pairs are
    %      applied to the GUI before GpEntrenarNormal_OpeningFunction gets called.  An
    %      unrecognized property name or invalid value makes property application
    %      stop.  All inputs are passed to GpEntrenarNormal_OpeningFcn via varargin.
    %
    %      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
    %      instance to run (singleton)".
    %
    % See also: GUIDE, GUIDATA, GUIHANDLES
    
    % Edit the above text to modify the response to help GpEntrenarNormal

    % Last Modified by GUIDE v2.5 28-Oct-2007 15:32:23

    % Begin initialization code - DO NOT EDIT

    gui_Singleton = 1;
    gui_State = struct('gui_Name',       mfilename, ...
                       'gui_Singleton',  gui_Singleton, ...
                       'gui_OpeningFcn', @GpEntrenarNormal_OpeningFcn, ...
                       'gui_OutputFcn',  @GpEntrenarNormal_OutputFcn, ...
                       'gui_LayoutFcn',  [] , ...
                       'gui_Callback',   []);
    if nargin & isstr(varargin{1})
        gui_State.gui_Callback = str2func(varargin{1});
    end

    if nargout
        [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
    else
        gui_mainfcn(gui_State, varargin{:});
    end

    % End initialization code - DO NOT EDIT


    global  T1;
    global  T2;
    global  T3;
    global  T4;
    global  T5;
    global  ang1;
    global  ang2;
    global  ang3;
    global  ang4;
    global  ang5;
    global  op;


    % --- Executes just before GpEntrenarNormal is made visible.
    
    function GpEntrenarNormal_OpeningFcn(hObject, eventdata, handles, varargin)
    % This function has no output args, see OutputFcn.
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)
    % varargin   command line arguments to GpEntrenarNormal (see VARARGIN)

    %Colocar Imagen de fondo
    back= imread('fondo.jpg'); %Leer imagen
    axes(handles.back); %Carga la imagen en background
    axis off;
    imshow(back); %Presenta la imagen

    angulos= imread('angulos.jpg'); %Leer imagen
    axes(handles.angulos); %Carga la imagen en background
    axis off;
    imshow(angulos); %Presenta la imagen
  
    
    archivar= imread('archivar.jpg'); %Leer imagen
    axes(handles.archivar); %Carga la imagen en background
    axis off;
    imshow(archivar); %Presenta la imagen
   
    handles.output = hObject;
    % Update handles structure
    guidata(hObject, handles);

    %Colocar Imagen brazo
    op=50;
    handles.Base=0;
    handles.Hombro=0;
    handles.Codo=0;
    handles.Pitch=0;
    handles.Roll=0;
    handles.Apertura=op; %op
    handles.BaseAnt=0;
    handles.HombroAnt=0;
    handles.CodoAnt=0;
    handles.PitchAnt=0;
    handles.RollAnt=0;
    handles.AperturaAnt=op; %op
    puerto='Com1';
    handles.Nombre='Posiciones.txt';
    handles.letra=1;
    handles.Posicion=0;
    
    guidata(hObject,handles);
    %% Movemos solo por seguridad... no seguridad del sistema sino para
    %% asegurar estar en home-.... jajajaja POR ESO DEBE SER    .... op,1,puerto....
    [d1,A1,A2,A3,A4,A5]=DirectoG(0,0,0,0,0,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
        T5=A1*A2*A3*A4*A5;
        T4=A1*A2*A3*A4;
        T3=A1*A2*A3;
        T2=A1*A2;
        T1=A1;
    
        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];
    axes(handles.Brazo); %Carga la imagen  
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    clc;    
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    axes(handles.Brazo1); %Carga la imagen    
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    clc;    
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    clc;
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    axes(handles.Brazo2); %Carga la imagen   
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    clc;    
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    clc;
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    axes(handles.Brazo3); %Carga la imagen   
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    clc;
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    clc;
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    %Stop(puerto);
    clc;
    
    handles.Archivo = fopen('Posiciones.txt','wb');
    % Choose default command line output for GpEntrenarNormal
    handles.output = hObject;
    
    % Update handles structure
    guidata(hObject, handles);

    % UIWAIT makes GpEntrenarNormal wait for user response (see UIRESUME)
    % uiwait(handles.figure1);


    % --- Outputs from this function are returned to the command line.
    function varargout = GpEntrenarNormal_OutputFcn(hObject, eventdata, handles)
    % varargout  cell array for returning output args (see VARARGOUT);
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)

    % Get default command line output from handles structure
    varargout{1} = handles.output;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%FIN INICIALIZAR%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Edits%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Creacion%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % --- Executes during object creation, after setting all properties.
    function Base_CreateFcn(hObject, eventdata, handles)
    % hObject    handle to Base (see GCBO)
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    empty - handles not created until after all CreateFcns called
    
    % Hint: edit controls usually have a white back on Windows.
    %       See ISPC and COMPUTER.
       if ispc
            set(hObject,'BackgroundColor','white');
       else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
       end

    function Hombro_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

    function Codo_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
    
    function Pitch_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Roll_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Apertura_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Puerto_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

    function nombrearchivo_CreateFcn(hObject, eventdata, handles)

        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Llamado%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    function Base_Callback(hObject, eventdata, handles)
        % hObject    handle to Base (see GCBO)
        % eventdata  reserved - to be defined in a future version of MATLAB
        % handles    structure with handles and user data (see GUIDATA)

        % Hints: get(hObject,'String') returns contents of Base as text
        %        str2double(get(hObject,'String')) returns contents of Base as a double

        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -126.5 )
            NewVal=-126.5;
        elseif ( NewVal > 126.5 )
            NewVal=126.5;
        end
        handles.Base=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Hombro_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -120 )
            NewVal=-120;
        elseif ( NewVal > 63 )
            NewVal=63;
        end     
        handles.Hombro=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Codo_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -90 )
            NewVal=-90;
        elseif ( NewVal > 90 )
            NewVal=90;
        end
        handles.Codo=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Pitch_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -250 )
            NewVal=-250;
        elseif ( NewVal > 40 )
            NewVal=40;
        end
        handles.Pitch=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Roll_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -180 )
            NewVal=-180;
        elseif ( NewVal > 180 )
            NewVal=180;
        end
        handles.Roll=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Apertura_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < 0 )
            NewVal= 0;
        elseif ( NewVal > 59 )
            NewVal= 59;
        end
        handles.Apertura=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Puerto_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        handles.Port=NewVal;
        handles.output = hObject;
        guidata(hObject, handles);

    function nombrearchivo_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        handles.Nombre=NewStrVal;        
        handles.output = hObject;
        guidata(hObject, handles);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Fin Edits%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Push Buttons%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % --- Executes on button press in pushbutton1. Ejecutar
    function pushbutton1_Callback(hObject, eventdata, handles)
    % hObject    handle to pushbutton1 (see GCBO)
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)

        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        
        switch (handles.port)
            case    1,
                puerto='Com1';
            case    2,
                puerto='Com2';
            case    3,
                puerto='Com3';
            case    4,
                puerto='Com4';
            case    5,
                puerto='Com5';
            case    6,
                puerto='Com6';
            case    7,
                puerto='Com7';
            case    8,
                puerto='Com8';
            case    9,
                puerto='Com9';
            otherwise
                puerto='Com1';
        end

        op=handles.Apertura;
    % Choose default command line output for GpEntrenarNormal
        handles.output = hObject;
    
    % Update handles structure
        guidata(hObject, handles);

    %Colocar Imagen brazo
        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
            T5=A1*A2*A3*A4*A5;
            T4=A1*A2*A3*A4;
            T3=A1*A2*A3;
            T2=A1*A2;
            T1=A1;

            x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
            y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
            z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];

        handles.BaseAnt=handles.Base;
        handles.HombroAnt=handles.Hombro;
        handles.CodoAnt=handles.Codo;
        handles.PitchAnt=handles.Pitch;
        handles.RollAnt=handles.Roll;
        handles.AperturaAnt=handles.Apertura;

    % Choose default command line output for GpEntrenarNormal
        handles.output = hObject;
    
    % Update handles structure
        guidata(hObject, handles);
    
        axes(handles.Brazo); %Carga la imagen en background
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        axes(handles.Brazo2); %Carga la imagen  
        clc;
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        clc;
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        clc;
        handles.output = hObject;
        guidata(hObject, handles);
            pause(6)
            Stop(puerto);
            pause(0.1)
            Stop(puerto);
        clc;
    % --- Executes on button press in pushbutton2.Simular
    function pushbutton2_Callback(hObject, eventdata, handles)
        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        switch (handles.port)
            case    1,
                puerto='Com1';
            case    2,
                puerto='Com2';
            case    3,
                puerto='Com3';
            case    4,
                puerto='Com4';
            case    5,
                puerto='Com5';
            case    6,
                puerto='Com6';
            case    7,
                puerto='Com7';
            case    8,
                puerto='Com8';
            case    9,
                puerto='Com9';
            otherwise
                puerto='Com1';
        end

        op=handles.Apertura;
        handles.output = hObject;
        guidata(hObject, handles);

        %Colocar Imagen brazo
        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,0,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
            T5=A1*A2*A3*A4*A5;
            T4=A1*A2*A3*A4;
            T3=A1*A2*A3;
            T2=A1*A2;
            T1=A1;

        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];

        % Choose default command line output for GpEntrenarNormal
            handles.output = hObject;

        % Update handles structure
            guidata(hObject, handles);

            axes(handles.Brazo); %Carga la imagen en background
            pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
            pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        clc;
        axes(handles.Brazo2); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        clc;
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        clc;
    % --- Executes on button press in Resetear.
    function Resetear_Callback(hObject, eventdata, handles)
        op=50;
        handles.Base=0;
        handles.Hombro=0;
        handles.Codo=0;
        handles.Pitch=0;
        handles.Roll=0;
        handles.Apertura=op; %op
        guidata(hObject,handles);

        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        switch handles.port
            case    1,
                puerto='Com1';
            case    2,
                puerto='Com2';
            case    3,
                puerto='Com3';
            case    4,
                puerto='Com4';
            case    5,
                puerto='Com5';
            case    6,
                puerto='Com6';
            case    7,
                puerto='Com7';
            case    8,
                puerto='Com8';
            case    9,
                puerto='Com9';
            otherwise
                puerto='Com1';
        end

        % Choose default command line output for GpEntrenarNormal
            handles.output = hObject;

        % Update handles structure
            guidata(hObject, handles);

        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
                T5=A1*A2*A3*A4*A5;
                T4=A1*A2*A3*A4;
                T3=A1*A2*A3;
                T2=A1*A2;
                T1=A1;

        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];


        handles.BaseAnt=handles.Base;
        handles.HombroAnt=handles.Hombro;
        handles.CodoAnt=handles.Codo;
        handles.PitchAnt=handles.Pitch;
        handles.RollAnt=handles.Roll;
        handles.AperturaAnt=handles.Apertura;
        axes(handles.Brazo); %Carga la imagen en background   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        axes(handles.Brazo2); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        clc;
        handles.output = hObject;
        guidata(hObject, handles);
        pause(10);
        Stop(puerto);
        
    % --- Executes on button press in Retorno.
    function Retorno_Callback(hObject, eventdata, handles)
        if (handles.Archivo ~= 0)
            fclose(handles.Archivo);
        end
        
        op=50;
        handles.Base=0;
        handles.Hombro=0;
        handles.Codo=0;
        handles.Pitch=0;
        handles.Roll=0;
        handles.Apertura=op; %op
        guidata(hObject,handles);

        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        switch handles.port
            case    1,
                puerto='Com1';
            case    2,
                puerto='Com2';
            case    3,
                puerto='Com3';
            case    4,
                puerto='Com4';
            case    5,
                puerto='Com5';
            case    6,
                puerto='Com6';
            case    7,
                puerto='Com7';
            case    8,
                puerto='Com8';
            case    9,
                puerto='Com9';
            otherwise
                puerto='Com1';
        end

        % Choose default command line output for GpEntrenarNormal
            handles.output = hObject;

        % Update handles structure
            guidata(hObject, handles);

        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);

        handles.BaseAnt=handles.Base;
        handles.HombroAnt=handles.Hombro;
        handles.CodoAnt=handles.Codo;
        handles.PitchAnt=handles.Pitch;
        handles.RollAnt=handles.Roll;
        handles.AperturaAnt=handles.Apertura;
        clc;
        handles.output = hObject;
        guidata(hObject, handles);
        pause(10);
        Stop(puerto);
        clear all; 
        close all;
        clc; 
        GMenu;


    % --- Executes on button press in Salvar.
    function Salvar_Callback(hObject, eventdata, handles)
        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        puerto=handles.Puerto;
        op=handles.Apertura;
        handles.letra=handles.letra;
        if (handles.Archivo == 0)
            handles.letra=30;
        end
        switch(handles.letra)
            case 1
               if(handles.Posicion==0) 
                    menu('Letra A -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra A -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra A -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra A -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra A -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 2
               if(handles.Posicion==0) 
                    menu('Letra B -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra B -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra B -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra B -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra B -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 3
               if(handles.Posicion==0) 
                    menu('Letra C -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra C -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra C -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra C -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra C -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 4
               if(handles.Posicion==0) 
                    menu('Letra D -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra D -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra D -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra D -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra D -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 5
                if(handles.Posicion==0) 
                    menu('Letra E -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra E -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra E -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra E -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra E -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 6
                 if(handles.Posicion==0) 
                    menu('Letra F -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra F -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra F -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra F -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra F -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 7
                 if(handles.Posicion==0) 
                    menu('Letra G -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra G -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra G -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra G -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra G -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 8
               if(handles.Posicion==0) 
                    menu('Letra H -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra H -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra H -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra H -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra H -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 9
               if(handles.Posicion==0) 
                    menu('Letra I -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra I -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra I -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra I -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra I -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 10
               if(handles.Posicion==0) 
                    menu('Letra J -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra J -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra J -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra J -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra J -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 11
               M = menu('Letra K -> Posicion 1 APRENDIDA','Listo');
               handles.letra=handles.letra+1;
            case 12
               if(handles.Posicion==0) 
                    menu('Letra K -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra K -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra K -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra K -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra K -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 13
               if(handles.Posicion==0) 
                    menu('Letra L -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra L -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra L -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra L -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra L -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 14
               if(handles.Posicion==0) 
                    menu('Letra M -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra M -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra M -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra M -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra M -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 15
               if(handles.Posicion==0) 
                    menu('Letra Ñ -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra Ñ -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra Ñ -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra Ñ -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra Ñ -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 16
               if(handles.Posicion==0) 
                    menu('Letra O -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra O -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra O -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra O -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra O -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 17
               if(handles.Posicion==0) 
                    menu('Letra P -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra P -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra P -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra P -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra P -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 18
               if(handles.Posicion==0) 
                    menu('Letra Q -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra Q -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra Q -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra Q -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra Q -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 19
               if(handles.Posicion==0) 
                    menu('Letra R -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra R -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra R -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra R -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra R -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 20
               if(handles.Posicion==0) 
                    menu('Letra S -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra S -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra S -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra S -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra S -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 21
               if(handles.Posicion==0) 
                    menu('Letra T -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra T -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra T -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra T -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra T -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 22
               if(handles.Posicion==0) 
                    menu('Letra U -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra U -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra U -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra U -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra U -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 23
               if(handles.Posicion==0) 
                    menu('Letra V -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra V -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra V -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra V -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra V -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 24
               if(handles.Posicion==0) 
                    menu('Letra W -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra W -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra W -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra W -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra W -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 25
               if(handles.Posicion==0) 
                    menu('Letra X -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra X -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra X -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra X -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra X -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 26
               if(handles.Posicion==0) 
                    menu('Letra Y -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra Y -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra Y -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra Y -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra Y -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 27
               if(handles.Posicion==0) 
                    menu('Letra Z -> Posicion 1 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==1) 
                    menu('Letra Z -> Posicion 2 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==2) 
                    menu('Letra Z -> Posicion 3 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==3) 
                    menu('Letra Z -> Posicion 4 APRENDIDA','Listo');
                    handles.Posicion=handles.Posicion+1;
               elseif(handles.Posicion==4) 
                    menu('Letra Z -> Posicion 5 APRENDIDA','Listo');
                    handles.Posicion=0;
                    handles.letra=handles.letra+1;
               end
            case 28
               M = menu('Alfabeto listo','Listo');
               
        end

        if (handles.Archivo ~= 0 && handles.letra<28)            
            [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,0,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
                T5=A1*A2*A3*A4*A5;
                T4=A1*A2*A3*A4;
                T3=A1*A2*A3;
                T2=A1*A2;
                T1=A1;
    
            for i=1:3,
                for j=1:4,
                    fprintf(handles.Archivo,'%6.4f %t',T5(i,j));
                end
                fprintf(handles.Archivo,'\n');
            end
        
            fprintf(handles.Archivo,'\n');
            fprintf(handles.Archivo,'\n');
        end
        
        handles.output = hObject;
        guidata(hObject, handles);
        

    function OpenFile_Callback(hObject, eventdata, handles)
        archivo=handles.Nombre;
        handles.Archivo = fopen(archivo,'wb');
        handles.output = hObject;
        guidata(hObject, handles);
        
    function CloseFile_Callback(hObject, eventdata, handles)
        if (handles.Archivo ~=0)
            fclose(handles.Archivo);
            handles.Archivo= 0;
        end
        handles.output = hObject;
        guidata(hObject, handles);
        
    function DeleteFile_Callback(hObject, eventdata, handles)
        if (handles.Archivo ~=0)
            fclose(handles.Archivo);
            handles.Archivo= 0;
        end
        archivo=handles.Nombre;
        delete(archivo);
        handles.output = hObject;
        guidata(hObject, handles);
        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Fin Push Buttons%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Funciones extras%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function y=pintar(T1,T2,T3,T4,T5,op,x,y,z,vera,verb)

    %     DibBase;
    %     Hombro(T1);
    %     CyM(T2);
    %     CyM(T3);
    %     Gripper(T5,op);
    %     plot3(x,y,z),
    %     grid on
    %     view([112.5,30])  

    axis([-700 700 -700 700 -1 700])
    xlabel('Eje X');
    ylabel('Eje Y');
    zlabel('Eje Z');
    hold;
    % define la plano base
    a=150;
    b=350;
    c=0;
    x0=[ a -a -a  a];
    y0=[ b  b -b -b];
    z0=[ c  c  c  c];
    w0=[ 1  1  1  1];
    fill3(x0,y0,z0,'k');
    % define circunferencia de la base
    ndiv=40;
    radio1=90.90;
    radio2=86.26;
    offset=193;
    x1=radio1*cos(0:(2*pi/ndiv):2*pi);
    y1=radio1*sin(0:(2*pi/ndiv):2*pi);
    z1=radio1*zeros(ndiv+1,1)';
    x2=radio2*cos(0:(2*pi/ndiv):2*pi);
    y2=radio2*sin(0:(2*pi/ndiv):2*pi);
    z2=offset*ones(ndiv+1,1)';
    for i=1:ndiv,
        fill3([x1(i) x2(i) x2(i+1) x1(i+1)],[y1(i) y2(i) y2(i+1) y1(i+1)],[z1(i) z2(i) z2(i+1) z1(i+1)],'c');
    end  

    T=T1;
    a=101.0;
    b=340-193;
    c=102.0;
    % dibuja base
    w(1,:)=[ a -a -a  a]; % datos para x
    w(2,:)=[ b  b  b  b]; % datos para y
    w(3,:)=[ c  c -c -c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    % dibuja tapa izquierda
    a=101.0;
    b=340-193;
    c=102.0;
    d=55;
    e=162;
    % dibuja lado izquierdo
    wl(1,:)=[ a  a   d   -a   -a ]; % datos para x
    wl(2,:)=[ b  b-d b-e  b-e  b ]; % datos para y
    wl(3,:)=[ c  c   c    c    c ]; % datos para z
    wl(4,:)=[ 1  1   1    1    1 ]; % 
    w2=T*wl;
    fill3(w2(1,1:5),w2(2,1:5),w2(3,1:5),'y');
    % dibuja lado derecho
    wl(1,:)=[  a  a   d   -a   -a ]; % datos para x
    wl(2,:)=[  b  b-d b-e  b-e  b ]; % datos para y
    wl(3,:)=[ -c -c  -c   -c   -c ]; % datos para z
    wl(4,:)=[  1  1   1    1    1 ]; % 
    w3=T*wl;
    fill3(w3(1,1:5),w3(2,1:5),w3(3,1:5),'y');

    T=T2;
    % define parametros del codo
    a=220; % largo del segmento
    b=35;  % ancho
    c=95; % desface del segmento
    % dibuja segmento 
    w(1,:)=[ -a  0  0 -a]; % datos para x
    w(2,:)=[ -b -b  b  b]; % datos para y
    w(3,:)=[ -c -c -c -c]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    w(1,:)=[-a  0  0 -a]; % datos para x
    w(2,:)=[-b -b  b  b]; % datos para y
    w(3,:)=[ c  c  c  c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'y');
    
    T=T3;
    % define parametros del codo
    a=220; % largo del segmento
    b=35;  % ancho
    c=95; % desface del segmento
    % dibuja segmento 
    w(1,:)=[ -a  0  0 -a]; % datos para x
    w(2,:)=[ -b -b  b  b]; % datos para y
    w(3,:)=[ -c -c -c -c]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    w(1,:)=[-a  0  0 -a]; % datos para x
    w(2,:)=[-b -b  b  b]; % datos para y
    w(3,:)=[ c  c  c  c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'y');
    
    T=T5;
    o=op;

    % define parametros del codo
    a=151;   % largo del segmento
    b=75.5;  % comienzo base gripper
    c=20.0;  % ancho de la base gripper
    d=15.0;	% ancho del gripper
    
    % dibuja segmento fondo
    w(1,:)=[  c -c -c  c]; % datos para x
    w(2,:)=[ -c -c  c  c]; % datos para y
    w(3,:)=[ -a -a -a -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'g');
    
    % dibuja segmento origen del gripper
    w(1,:)=[ -c   -c     c     c  ]; % datos para x
    w(2,:)=[  c   -c    -c     c  ]; % datos para y
    w(3,:)=[ -a+b -a+b  -a+b  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'g');
    % dibuja segmento tapa superior
    w(1,:)=[ -c -c  c  c]; % datos para x
    w(2,:)=[  c  c  c  c]; % datos para y
    w(3,:)=[ -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w3=T*w;
    fill3(w3(1,1:4),w3(2,1:4),w3(3,1:4),'g');
    % dibuja segmento tapa inferior
    w(1,:)=[ -c -c  c  c]; % datos para x
    w(2,:)=[ -c -c -c -c]; % datos para y
    w(3,:)=[  -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w4=T*w;
    fill3(w4(1,1:4),w4(2,1:4),w4(3,1:4),'g');
    % dibuja segmento tapa lateral izquierda
    w(1,:)=[  c c  c c]; % datos para x
    w(2,:)=[  -c  -c  c c]; % datos para y
    w(3,:)=[ -a  -a+b -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w5=T*w;
    fill3(w5(1,1:4),w5(2,1:4),w5(3,1:4),'g');
    % dibuja segmento tapa lateral derecha
    w(1,:)=[  -c  -c  -c  -c]; % datos para x
    w(2,:)=[ -c  -c c c]; % datos para y
    w(3,:)=[  -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w5=T*w;
    fill3(w5(1,1:4),w5(2,1:4),w5(3,1:4),'g');
    
    % dibuja plano del fondo del gripper
    w(1,:)=[ -o -o  o  o]; % datos para x
    w(2,:)=[  d -d -d  d]; % datos para y
    w(3,:)=[ -a+b  -a+b  -a+b  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w6=T*w;
    fill3(w6(1,1:4),w6(2,1:4),w6(3,1:4),'g');

    % dibuja plano izquierdo del gripper
    w(1,:)=[ -o -o -o -o]; % datos para x
    w(2,:)=[  d d -d -d]; % datos para y
    w(3,:)=[  -a+b  0  0  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w7=T*w;
    fill3(w7(1,1:4),w7(2,1:4),w7(3,1:4),'g');
    % dibuja plano derecho del gripper
    w(1,:)=[  o  o  o  o]; % datos para x
    w(2,:)=[  d d -d -d]; % datos para y
    w(3,:)=[  -a+b  0  0  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w8=T*w;
    fill3(w8(1,1:4),w8(2,1:4),w8(3,1:4),'g');
    
    plot3(x,y,z),
    grid on
    view([vera,verb])