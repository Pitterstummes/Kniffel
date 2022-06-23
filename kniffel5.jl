#Initializing
using DelimitedFiles
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
    caseline = casepoint[case,:]
    #println(case, caseline)
    return case, caseline
end