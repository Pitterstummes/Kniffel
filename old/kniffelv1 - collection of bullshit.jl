#this is some scuffed shit, good luck understanding anything LOL

#Goals of this program are self contained playing of kniffel and also writing down into the analysis sheet + statistical analysis
#splitting in 2 parts: 1. Playing the game and assigning results to the analysis sheet and 2. calculating scores

#initializing
scoreboard_start = ["gamenumber", "ones", "twos", "threes", "fours", "fives", "sixes", "sum1", "bonus", "total 1", "pair", "doublepair", "triplet",
 "quadruplet", "full house", "small street", "big street", "kniffel", "chance", "total 2", "total"]
scoreboard = scoreboard_start
game0 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
game1 = game0
#game1 = [-1, 3, 6, 9, 12, 15, 18, -1, -1, -1, 12, 22, 18, 24, 30, 25, 40, 50, 22, -1, -1]

show(stdout, "text/plain", scoreboard)

n = 1 #how many games would you like to play?
for i in 1:n
    game1[1] = i
    finished = 0
    for t in 1:16 # =16, 15 times rolling and 1 time checking if finished
        #throwing some dice...you allways have to start with a first throw #in this approach, first, one single throw (not 3) is getting realized
        throw1 = rand(1:6,5)
        throw1_count = [count(==(1), throw1), count(==(2), throw1), count(==(3), throw1), count(==(4), throw1), count(==(5), throw1), count(==(6), throw1)]
        #2 sorting regarding multiplicity
        count1 = maximum(throw1_count)
        if count1 == 5 #kniffel
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            println("kniffel of ",number,"s! - you are lucky")
            if game1[18] == -1 #enter points in game1
                game1[18] = 50
                println("added a kniffel")
            elseif game[18] == 0
                println("kniffel got allready cancelled :(")
                println("mr programmer, you got to fix this case!") #fix needed since this case does not fill any field
            else
                game1[18] = game1[18] + 50
                println("wow, another kniffel!")
                if game1[number+1] == -1
                    game1[number+1] = sum(throw1)
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[13] == -1
                    game1[13] = 3*number
                elseif game1[14] == -1
                    game1[14] = 4*number
                elseif game1[19] == -1
                    game1[19] == sum(throw1)
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                end
            end
        elseif count1 == 4 #quadruplet
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            println("quadruplet with ",number,"s!")
            if game1[number+1] == -1 #enter points in game1
                game1[number+1] = 4*number
                println("added a quadrupel")
            else
                if game1[14] == -1
                    game1[14] = 4*number
                elseif game1[13] == -1
                    game1[13] = 3*number
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[19] == -1
                    game1[19] == sum(throw1)
                elseif game1[18] == -1
                    game[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                end
            end
        elseif count1 == 3 #triplet, check for full house, 2 pair?---------------------------------------------------
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            if count(==(0),throw1_count) == 4
                println("full house!")
                if game1[15] == -1
                    game1[15] = 30
                    println("added full house!")
                else
                    if game1[1+number] == -1
                        game1[1+number] = 3*number
                    elseif game1[13] == -1
                        game1[13] = number*3
                    elseif game1[11] == -1
                        game1[11] = 2*number
                    elseif game1[19] == -1
                        game1[19] = sum(throw1)
                    elseif game1[18] == -1
                        game1[18] = 0
                    elseif game1[17] == -1
                        game1[17] = 0
                    elseif game1[16] == -1
                        game1[16] = 0
                    elseif game1[12] == -1
                        game1[12] = 0
                    elseif game1[14] == -1
                        game1[14] = 0
                    end
                end
            else
                println("triplet with ",number,"s!")
                if game1[1+number] == -1
                    game1[1+number] = 3*number
                elseif game1[13] == -1
                    game1[13] = number*3
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                end
            end
        elseif length(findall(x -> x == maximum(throw1_count), throw1_count)) == 2 #doublepair
            numbers = findall(x -> x == maximum(throw1_count), throw1_count)
            println("doublepair with ",numbers[1],"s and ",numbers[2],"s!")
            if game1[12] == -1
                game1[12] = (2*numbers[1]) + (2*numbers[2])
            elseif game1[11] == -1
                game1[11] = sort(numbers)[2]*2
            elseif game1[19] == -1
                game1[19] = sum(throw1)
            elseif game1[1+sort(numbers)[1]] == -1
                game1[1+sort(numbers)[1]] = 2*sort(numbers)[1]
            elseif game1[1+sort(numbers)[2]] == -1
                game1[1+sort(numbers)[2]] = 2*sort(numbers)[2]
            elseif game1[18] == -1
                game1[18] = 0
            elseif game1[17] == -1
                game1[17] = 0
            elseif game1[15] == -1
                game1[15] = 0
            elseif game1[16] == -1
                game1[16] = 0
            elseif game1[12] == -1
                game1[12] = 0
            elseif game1[14] == -1
                game1[14] = 0
            end
        elseif count1 == 2 #pair, check for street!
            number = findfirst(x -> x == maximum(throw1_count), throw1_count) #number of the pair
            missingnumbers = findall(==(minimum(throw1_count)), throw1_count) #2 missing numbers
            if 1 in missingnumbers && 2 in missingnumbers || 5 in missingnumbers && 6 in missingnumbers
                println("pair of ",number,"s within a small street!")
                if game1[16] == -1
                    game1[16] = 25
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[1+number] == -1
                    game1[1+number] = 2*number
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                end
            elseif 1 in missingnumbers && 6 in missingnumbers
                println("pair of ",number,"s within a small street, perfect go for big street")
                if game1[16] == -1
                    game1[16] = 25
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[1+number] == -1
                    game1[1+number] = 2*number
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                end
            else
                println("just a pair of ",number,"s")
                if game1[11] == -1
                    game1[11] = 2*number
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[1+number] == -1
                    game1[1+number] = 2*number
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                end
            end
        elseif count1 == 1 #trash, street?
            missingnumber =  argmin(throw1_count)
            if missingnumber == 1 || missingnumber == 6
                println("big street!")
                if game1[17] == -1
                    game1[17] = 40
                elseif game1[16] == -1
                    game1[16] = 25
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[11] == -1
                    game1[11] = 0
                else
                    if game1[2] == -1 && missingnumber == 6
                        game1[2] = 1
                    elseif game1[3] == -1
                        game1[3] = 2
                    elseif game1[4] == -1
                        game1[4] = 3
                    elseif game1[5] == -1
                        game1[5] = 4
                    elseif game1[6] == -1
                        game1[6] = 5
                    elseif game1[7] == -1 && missingnumber == 1
                        game1[7] = 6
                    end
                end
            elseif missingnumber == 2 || missingnumber == 5
                println("small street!")
                if game1[16] == -1
                    game1[16] = 25
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[11] == -1
                    game1[11] = 0
                else
                    if game1[2] == -1
                        game1[2] = 1
                    elseif game1[3] == -1 && missingnumber == 5
                        game1[3] = 2
                    elseif game1[4] == -1
                        game1[4] = 3
                    elseif game1[5] == -1
                        game1[5] = 4
                    elseif game1[6] == -1 && missingnumber == 2
                        game1[6] = 5
                    elseif game1[7] == -1
                        game1[7] = 6
                    end
                end
            else
                println("unlucky, that's a garbage throw")
                if game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[2] == -1 && 1 in throw1
                    game1[2] = 1
                elseif game1[3] == -1 && 2 in throw1
                    game1[2] = 2
                elseif game1[4] == -1 && 3 in throw1
                    game1[2] = 3
                elseif game1[5] == -1 && 4 in throw1
                    game1[2] = 4
                elseif game1[6] == -1 && 5 in throw1
                    game1[2] = 5
                elseif game1[7] == -1 && 6 in throw1
                    game1[2] = 6
                elseif game1[18] == -1
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[14] == -1
                    game1[14] = 0
                elseif game1[13] == -1
                    game1[13] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[11] == -1
                    game1[11] = 0
            end
        end

        if -1 in game1 #checking if game has finished yet
            println("game has not finished yet..")
            if -1 in game1[2:7] #checking if first part finished yet
                println("part 1 not finished yet..")
            else
                if game1[8] == -1 #so this (calculation of first part) just happens one time
                    println("part 1 finished.")
                    game1[8] = sum(game1[2:7])
                    if game1[8] >= 63
                        game1[9] = 37
                        game1[10] = game1[8] + game1[9]
                    else
                        game1[9] = 0
                        game1[10] = game1[8]
                    end
                end
            end
            if -1 in game1[11:19] #checking if second part finished yet
                println("part 2 not finished yet..")
            else
                if game1[20] == -1 #so this just happens one time
                    println("part 2 finished.")
                    game1[20] = sum(game1[11:19])
                end
            end
            if game1[10] != -1 && game1[20] != -1 && game1[21] == -1  #calculating the total points just one time
                println("calculating final result..")
                game1[21] = game1[10] + game1[20]
                scoreboard = hcat(scoreboard,game1)
                println("added game ",i, " to the scoreboard.") ##remove later
            end
        else
            if finished == 0
                scoreboard = hcat(scoreboard,game1)
                println("added game ",i, " to the scoreboard.")
                finished = 1
            end
        end
    end
    game1 = game0
end
end

display(scoreboard)
println(game1)


#testrange kniffel go -> 45/1000 games gives a kniffel if going for it.
kniffelscoreboard = ["Gamenumber", "Kniffelnumber", "dicecount", "success?"]
kniffelsum = 0
for j in 1:100
    kniffelcount = 0
    for i in 1:10000
        kniffelthrow1 = rand(1:6,5)
        kniffelthrow1_count = [count(==(1), kniffelthrow1), count(==(2), kniffelthrow1), count(==(3), kniffelthrow1), count(==(4), kniffelthrow1),
         count(==(5), kniffelthrow1), count(==(6), kniffelthrow1)]
        number = findfirst(x -> x == maximum(kniffelthrow1_count), kniffelthrow1_count) #number
        count1 = maximum(kniffelthrow1_count) #count
        kniffelthrow2 = rand(1:6,5-count1)
        kniffelthrow2_count = [count(==(1), kniffelthrow2), count(==(2), kniffelthrow2), count(==(3), kniffelthrow2), count(==(4), kniffelthrow2),
         count(==(5), kniffelthrow2), count(==(6), kniffelthrow2)]
        count2 = count1 + kniffelthrow2_count[number]
        kniffelthrow3 = rand(1:6,5-count2)
        kniffelthrow3_count = [count(==(1), kniffelthrow3), count(==(2), kniffelthrow3), count(==(3), kniffelthrow3), count(==(4), kniffelthrow3),
         count(==(5), kniffelthrow3), count(==(6), kniffelthrow3)]
        count3 = count2 + kniffelthrow3_count[number]
        if count3 == 5
            kniffelcount = kniffelcount+1
        end
        #kniffelscoreboardadd = []
        #kniffelscoreboard = hcat(kniffelscoreboard,kniffelscoreboardadd)
    end
    kniffelsum = kniffelsum + kniffelcount
    println(kniffelsum/j)
end

#testrange for general throws
#first throw
for i in 1:1
    throw1 = rand(1:6,5)
    throw1_count = [count(==(1), throw1), count(==(2), throw1), count(==(3), throw1), count(==(4), throw1), count(==(5), throw1), count(==(6), throw1)]
    #2 sorting regarding multiplicity
    count1 = maximum(throw1_count)
    if count1 == 5 #kniffel
        number = findfirst(x -> x == maximum(throw1_count), throw1_count)
        println("kniffel of ",number,"s! - you are lucky")
    elseif count1 == 4 #quadruplet
        number = findfirst(x -> x == maximum(throw1_count), throw1_count)
        println("quadruplet with ",number,"s!")
    elseif count1 == 3 #triplet, check for full house
        number = findfirst(x -> x == maximum(throw1_count), throw1_count)
        if count(==(0),throw1_count) == 4
            println("full house!")
        else
            println("triplet with ",number,"s!")
        end
    elseif length(findall(x -> x == maximum(throw1_count), throw1_count)) == 2 #doublepair
        numbers = findall(x -> x == maximum(throw1_count), throw1_count)
        println("doublepair with ",numbers[1],"s and ",numbers[2],"s!")
    elseif count1 == 2 #pair, check for street!
        number = findfirst(x -> x == maximum(throw1_count), throw1_count) #number of the pair
        missingnumbers = findall(==(minimum(throw1_count)), throw1_count) #2 missing numbers
        if 1 in missingnumbers && 2 in missingnumbers || 5 in missingnumbers && 6 in missingnumbers
            println("pair of ",number,"s within a small street!")
        elseif 1 in missingnumbers && 6 in missingnumbers
            println("pair of ",number,"s within a small street, perfect go for big street")
        else
            println("just a pair of ",number,"s")
        end
    elseif count1 == 1 #trash, street?
        missingnumber =  argmin(throw1_count)
        if missingnumber == 1 || missingnumber == 6
            println("big street!")
        elseif missingnumber == 2 || missingnumber == 5
            println("small street!")
        else
            println("unlucky, that's a garbage throw")
        end
    end
    println(throw1_count)
end

findall(x -> x == argmin(throw1_count), throw1_count)
println(throw1)
println(throw1_count)
argmin(throw1_count)
findmin(throw1_count)
findall(==(minimum(throw1_count)), throw1_count)
findall(x -> x == maximum(throw1_count), throw1_count)



display(kniffelthrow2)
display(kniffelthrow2_count)
display(hcat(kniffelthrow1_count,kniffelthrow2_count,kniffelthrow3_count))
display(kniffelscoreboard)
