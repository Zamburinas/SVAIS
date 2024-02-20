%
% Funcion que lee un fichero de test almacenado en binario con la precision
% indicada como parametro de entrada
%
% Parametros de entrada:
% NombreFichero: nombre del fichero que se va a leer.
% FlagDatosComplejos: flag que indica si la señal de salida se entregara en
% formato complejo (1) o en formato real (0).
% Tipo: precision de los datos que se leen del fichero.  Ver la funcion fread
% NumeroMuestras: numero de muestras que se van a leer.  Se admite el valor
% Inf, que indica que se lee el fichero completo.
% Orden: indica el orden de las muestras en el fichero. Puede tomar los
% valores 'QI', indicando que las componentes en cuadratura estan situadas
% en las posiciones 1,3,5,7 y las componentes en fase estan situadas en
% 2,4,6,... o 'IQ' que es la ordenacion opuesta.
%
% Parametros de salida:
% X: vector de datos que contiene los valores leidos del fichero de señal
%
function X = lee_fichero_test(NombreFichero,FlagDatosComplejos,Tipo,NumeroMuestras,Orden)

if (nargin < 3) | (nargin > 5)
  X = [];
  error('Numero de parametros de entrada incorrecto');
end %if

if nargin == 3
  NumeroMuestras = inf;
  Orden = 'IQ';
end %if

if nargin == 4
  Orden = 'IQ';
end %if

numMuestras = NumeroMuestras;
if FlagDatosComplejos == 1
  numMuestras = 2*NumeroMuestras;
end

fid = fopen(NombreFichero,'r');
if fid == -1
  X = [];
  error(['Imposible abrir el fichero ' NombreFichero]);
end %if
x = fread(fid,numMuestras,Tipo);
fclose(fid);

if FlagDatosComplejos == 1
  if mod(length(x),2) == 1
    x = x(1:end-1);
  end %if
  if strcmp(upper(Orden),'IQ') == 1
    X = complex(x(1:2:end),x(2:2:end));
  elseif strcmp(upper(Orden),'QI') == 1
    X = complex(x(2:2:end),x(1:2:end));
  end
else
  X = x;
end %if