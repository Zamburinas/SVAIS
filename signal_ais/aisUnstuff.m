function [bitsOut] = aisUnstuff(bitsIn)

onesCount=0;
bitsIn=double(bitsIn);
bitsOut=zeros(length(bitsIn),1);
bitsOutIdx=1;
for ii=1:length(bitsIn)
%     disp(bitsIn(ii));
    if onesCount<5
        bitsOut(bitsOutIdx)=bitsIn(ii);
        bitsOutIdx=bitsOutIdx+1;
    end
    if bitsIn(ii)==1
        onesCount=onesCount+1;
    else
        onesCount=0;
    end
end
bitsOutIdx=min(length(bitsIn),bitsOutIdx);
bitsOut=bitsOut(1:bitsOutIdx);

