function y = wola(x,N)

if (ndims(x) > 2) | (prod(size(x)) > length(x))
  error('x debe ser un vector fila o columna');
  y = [];
  return;
end %if

if (N == 0)
  error('N debe ser mayor que 0');
  y = [];
  return;
end % if  

% Proceso

L = length(x);

if (N >= L)
  y = x;
  return;
end %if

M = ceil(L/N);  % Factor de WOLA
aux = zeros(M*N,1);
aux(1:L) = x(:);
y = sum(reshape(aux,N,M),2);
