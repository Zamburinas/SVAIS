function Y = semavg(X,M)
  
if nargin ~= 2
  error('Numero de parametros de entrada erroneo');
  return;
end %if

if isempty(X)
  error('El parametro X esta vacio');
  return
end %if

if (ndims(X) > 2) | ((size(X,1) > 1) & (size(X,2) > 1))
  error('El parametro X debe ser una matriz unidimensional');
  return
end %if

if isempty(M)
  error('El parametro M esta vacio');
  return
end %if

if (prod(size(M)) > 1)
  error('El parametro M debe ser un escalar');
  return;
end %if

if (length(X) < M/2)
	error('Numero de muestras del buffer de entrada incorrecto');
  return;
end %if

n = prod(size(X));
xx = X(:);
if mod(M,2) == 1
  x = [xx(floor((M-1)/2)+1:-1:2);xx;xx(n-1:-1:n-floor((M-1)/2))];
else
  x = [xx(floor(M/2)+1:-1:2);xx;xx(n-1:-1:n-floor(M/2)+1)];
end %if
y = conv(ones(M,1)/M,x);
Y = y(M:M-1+n);

% ind = zeros(M,n);
% 
% for ii = 0:M-1
%   ind(ii+1,:) = (0:n-1)-floor((M-1)/2)+ii;
% end %for
% 
% ind = abs(ind);
% [ii,jj] = find(ind > n-1);
% ind(ii + M*(jj-1)) =  2*(n-1)-ind(ii + M*(jj-1));
% ind = ind +1;
% 
% % Si hay NaNs, los obviamos considerando solo aquellos valores que no son
% % NaN
% % matriz = X(ind);
% % flags = (isnan(matriz) == 0);
% % N = sum(flags,1);
% % indFlags = find(flags == 0);
% % matriz(indFlags) = 0;
% % Y = sum(matriz,1)./N;
% 
% Y = sum(X(ind))/M;
% Y = Y(:);

