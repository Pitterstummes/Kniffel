#Initializing
using DelimitedFiles
using Plots
#cd("C:\\Users\\StandardUser\\Documents\\Julia\\Kniffel")

#Loading 
casepoint = readdlm("casepointsheetexpandnoheader.dat",Int64) #board with all possibilities and corresponding points
#assignment: D1	D2	D3	D4	D5	C1	C2	C3	C4	C5	C6	1s	2s	3s	4s	5s	6s	1P	2P	Tri	Qua	FH	SS	BS	KN	CH
#todo: generate groups of equal points (2*2, 2*3, ...)

#functions
function firstthrow() #first throw: Output 5 element vector with numbers from 1 to 6
    firstthrow = sort(rand(1:6,5),rev=true)
    return firstthrow
end

function throw_count(throw) #count dice: Output 6 element with numbers from 1 to 5 ##maybe not even needed!!!
    throw_count = [count(==(1), throw), count(==(2), throw), count(==(3), throw), count(==(4), throw), count(==(5), throw), count(==(6), throw)]
    return throw_count
end

function getcase_d(throw) #getcase: Output the actual of all 252 cases for the input throw, also the corresponding casepoint line
    case = nothing
    for i in 1:length(casepoint[:,1])
        if throw == casepoint[i,1:5]
            case = i
            break
        end
    end
    #caseline = casepoint[case,:]
    #println(case, caseline)
    return case#, caseline
end

#testing
getcase_d(firstthrow())

function getprop252(actualthrow)
    actualcount = throw_count(actualthrow)
    prop252 = zeros(252)
    intermed = zeros(Int8,6)
    for i = 1:252
        availablethrows = 0
        for j = 1:6
            intermed[j] = actualcount[j]-casepoint[i,5+j]
            if intermed[j] > 0
                availablethrows += intermed[j]
            end
        end
        if availablethrows == 0
            prop252[i] = 1
        elseif availablethrows == 1
            prop252[i] = 1/6
        elseif availablethrows == 2
            if -2 in intermed
                    prop252[i] = 1/36
            else
                    prop252[i] = 1/18
            end
        elseif availablethrows == 3
            if -3 in intermed
                    prop252[i] = 1/216
            elseif -2 in intermed
                    prop252[i] = 1/72
            else
                    prop252[i] = 1/36
            end
        elseif availablethrows == 4
            if -4 in intermed
                    prop252[i] = 1/1296
            elseif -3 in intermed
                    prop252[i] = 1/324
            elseif -2 in intermed && -1 ∉ intermed
                    prop252[i] = 1/216
            elseif -2 in intermed && -1 in intermed
                    prop252[i] = 1/108
            else
                    prop252[i] = 1/54
            end
        elseif availablethrows == 5
            if -5 in intermed
                    prop252[i] = 1/7776
            elseif -4 in intermed
                    prop252[i] = 5/7776
            elseif -3 in intermed && -2 in intermed
                    prop252[i] = 10/7776
            elseif -3 in intermed && -1 in intermed
                    prop252[i] = 20/7776
            elseif count(==(2), intermed) == 2
                    prop252[i] = 30/7776
            elseif count(==(2), intermed) == 1
                    prop252[i] = 60/7776
            else
                    prop252[i] = 20/1296
            end   
        end
    end
    return prop252
    #return nothing
end

propmatrix = zeros(252,252)

for i = 1:252
    propmatrix[:,i] = getprop252(casepoint[i,1:5])
end


propmatrix
open("propmatrix.txt","w") do io
    writedlm(io,propmatrix)
end
