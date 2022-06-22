#goal is to calculate possibilities for certain cases which are connected to certain points

#generating all 252 possible cases - this is allready in the casepointsheet.dat
cases252 = ones(Int,252,5)
k,l,m,n,o = 1,1,1,1,1
for i in 2:252
        k = k+1
        if k==7
                l=l+1
                k=l
        end
        if l==7
                m=m+1
                l=m
                k=l
        end
        if m==7
                n=n+1
                m=n
                l=m
                k=l
        end
        if n==7
                o=o+1
                n=o
                m=n
                l=m
                k=l
        end

        cases252[i,1] = k
        cases252[i,2] = l
        cases252[i,3] = m
        cases252[i,4] = n
        cases252[i,5] = o
end
show(stdout, "text/plain", cases252)

#random stuff - need a throw to compare
throw1 = sort(rand(1:6,5))
println(throw1)
prop252 = zeros(252)
yyy = sallsaved

#calculating the propability array to get to yyy252 within the next throwing round - dismissed
for j in 1:252
        for i in 1:5
                if throw1[i] in yyy[j,:]
                          pos = findfirst(==(throw1[i]), yyy[j,:])
                          yyy[j,pos] = 0
                end
        end
        if 0 in yyy[j,:]
                target = length(unique(yyy[j,:]))-1
        else
                target = length(unique(yyy[j,:]))
        end
        if target == 0 || target == 1
                retard = 1
        elseif target == 2
                retard = 3
        elseif target == 3
                retard = 6
        elseif target == 4
                retard = 24
        end
        countdice = count(!=(0),yyy[j,:])
        prop252[j] = (1/6)^countdice*retard
end

#visualizing the propability from previous step
show(stdout, "text/plain", prop252)
using Plots
plot(1:252,prop252,yaxis=:log)
println(throw1)

scores = zeros(Int,252,1)
#Idea ist to create a Array with Case/252, followed by all possible point constellations afterwards.
casepointsheetheader = "Casenumber", "Actual Number 1", "Actual Number 2", "Actual Number 3", "Actual Number 4", "Actual Number 5",  "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
 "Pair", "Doublepair", "Triplet", "Quadruplet", "Full House", "Small Street", "Big Street", "Kniffel", "Chance"

#generation of the casepointsheet - allready done
casepointsheet = zeros(Int,252,21)
casepointsheet[1,20] = 50
for i in 1:252
        for j in 1:6
                if count(==(j),casepointsheet[i,2:6]) >= 2
                        casepointsheet[i,13] = 2*j
                end
        end
end
show(stdout, "text/plain", casepointsheet)

#changing in right directory and loading casepointsheet as any matrix
using DelimitedFiles
pwd()
cd("C:\\Users\\StandardUser\\Documents\\Julia\\Kniffel")
#w-r-i-t-e-d-l-m-(-"-c-a-s-e-p-o-i-n-ts-h-e-e-t-.-d-a-t-"-,- -c-a-s-e-p-o-i-n-t-s-h-e-e-t-) #disabled so casepointsheet does not get overwritten
readmat = readdlm("casepointsheet.dat")
readmatexpand = readdlm("casepointsheetexpandnoheader.dat")
show(stdout, "text/plain", readmat)
show(stdout, "text/plain", readmatexpand)


#generating a throw and obtaining prop252
throw1 = sort(rand(1:6,5),rev=true)
throw1_count = [count(==(1), throw1), count(==(2), throw1), count(==(3), throw1), count(==(4), throw1), count(==(5), throw1), count(==(6), throw1)]
# println(throw1)
println(throw1_count)
for i in 2:253
        if throw1 == readmat[i,2:6]
        println("Actual case is case ",readmat[i,1]," in line ",i)
        end
end

#expanded part for the readmatexpand
throwcount252 = zeros(Int,252,6)
for i in 1:252
        for j in 1:6
                throwcount252[i,j] = count(==(j), cases252[i,:])
        end
end
show(stdout, "text/plain", throwcount252)
show(stdout, "text/plain", cases252)
writedlm("throwcount252.dat",throwcount252)

#generating the subtraction of 2 throwcounts
prop252 = zeros(6,1)
for n in 1:1
        intermed = zeros(Int,1,6)
        for i in 1:252
                for j in 1:6
                        intermed[j] = throw1_count[j]-readmatexpand[i,j+6]
                end
                availablethrows = count(>(0), intermed)
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
end

#testing propabilites
n = 100000
j = 0
uss = zeros(100,1)
for u in 1:100
        j = 0
        for i in 1:n
                tes = sort(rand(1:6,5))
                if [4,5,6,6,6] == tes
                        j = j+1
                end
                if i == n
                        uss[u] = j/n
                end
        end
end
println(sum(uss)/100)
