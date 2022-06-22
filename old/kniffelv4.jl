#loading needed pacakages
using DelimitedFiles

#changing in right folder for bigmatrix
pwd()
cd("C:\\Users\\paulk\\Documents\\Programmieren\\Julia") #homepc
cd("C:\\Users\\StandardUser\\Documents\\Julia\\Kniffel") #unipc

#import and visualizing matirx
#Nr D1 D2 D3 D4 D5 C1 C2 C3 C4 C5 C6 1s 2s 3s 4s 5s 6s 1P 2P Tri Qua FH SS BS KN CH
#1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20  21  22 23 24 25 26 27
readmatexpand = readdlm("casepointsheetexpandnoheader.dat",Int)
show(stdout, "text/plain", readmatexpand)

#Initializing scoreboard
scoreboard_start = ["Gamenumber", "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes", "Sum1", "Bonus", "Total 1", "Pair", "Doublepair", "Triplet",
 "Quadruplet", "Full House", "Small Street", "Big Street", "Kniffel", "Chance", "Total 2", "Total"] #21 entrys for left side legend
game0 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] #reference: empty scoresheet (-1 means empty since 0 is needed for xed fields)
scoreboard = scoreboard_start #clear scoreboard
game = game0 #clear scoresheet

#Visualization of Scoreboard
function showboard(g)
    show(stdout, "text/plain", hcat(scoreboard[:,1],scoreboard[:,g+1]))
end
show(stdout, "text/plain", leftgames)
showboard(5) #shows the scoreboard at gamenumber = functionposition

#generating a throw
throw1 = sort(rand(1:6,5),rev=true)
throw1_count = [count(==(1), throw1), count(==(2), throw1), count(==(3), throw1), count(==(4), throw1), count(==(5), throw1), count(==(6), throw1)]
println(throw1)
println(throw1_count)

#generating propability for all 252 cases
prop252 = zeros(252)
for n in 1:1
        intermed = zeros(Int,6)
        for i in 1:252
                for j in 1:6
                        intermed[j] = throw1_count[j]-readmatexpand[i,j+6]
                end
                availableindex = findall(>(0), intermed)
                availablethrows = sum(intermed[availableindex])
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
                                prop252[i] = 1/1555.2
                        elseif -3 in intermed && -2 in intermed
                                prop252[i] = 1/777.6
                        elseif -3 in intermed && -1 in intermed
                                prop252[i] = 1/388.8
                        elseif count(==(2), intermed) == 2
                                prop252[i] = 1/259.2
                        elseif count(==(2), intermed) == 1
                                prop252[i] = 1/129.6
                        else
                                prop252[i] = 1/64.8
                        end
                end
        end
end

show(stdout, "text/plain", prop252)
findfirst(==(1),prop252)
println(readmatexpand[105,:])

max = zeros(252,1)
for i in 1:252
        max[i] = maximum(readmatexpand[i,13:27])
end
pointpropability = prop252.*max
findfirst(>(10), pointpropability)
println(readmatexpand[97,:])
using Plots
plot(1:252,pointpropability,xlabel = "case", ylabel = "pointpropability",=:dot)

#propability for certain events like triplet, kniffel, ..
#finding the corresponding cases in order do get the right propabilitys
keepcases = zeros(252,15)
actualcase = findfirst(==(1),prop252)
for i in 1:252
        if 3 in readmatexpand[i,2:6] && count(==(3),readmatexpand[i,2:6]) == 3
                println("Is case for line ",i)
        end
end



#Runparameters
numberofgames = 1 #how many games would you like to play?
totalthrows = 3 # throws per round, normally=3: which sick bastard would not abide by the normal rules, however any number is possible (hopefully)

for i in 1:numberofgames #till end
    game[1] = i #write gamenumber in scoresheet
    for r in 1:15 # 15 fields to fill per game, r stands for round, do not change

        for t in 1:totalthrows #typical 3, end of this loop is writing a score into the scoresheet
            throw = rand(1:6,5)
            println(throw)
            throw_count = [count(==(1), throw), count(==(2), throw), count(==(3), throw), count(==(4), throw), count(==(5), throw), count(==(6), throw)]
            throwanalysis(throw_count)
        end
        if r==15 #calculating scores when game has finished
            game[8] = sum(game[2:7])
            if game[8] >= 63
                game[9] = 37
                game[10] = game[8] + 37
            else
                game[9] = 0
                game[10] = game[8]
            end
            game[20] = sum(game[11:19])
            game[21] = game[10] + game[20]
            scoreboard = hcat(scoreboard,game)
            println("Added game ",i," to the scoreboard")
            game = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] #reseting scoresheet for upcoming games
        end
    end
end
