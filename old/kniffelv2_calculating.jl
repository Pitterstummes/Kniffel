#Goals of this program are self contained playing of kniffel and also writing down into the analysis sheet + statistical analysis

#after initializing parameters, the

#initializing
scoreboard_start = ["gamenumber", "ones", "twos", "threes", "fours", "fives", "sixes", "sum1", "bonus", "total 1", "pair", "doublepair", "triplet",
 "quadruplet", "full house", "small street", "big street", "kniffel", "chance", "total 2", "total"]
game0 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
scoreboard = scoreboard_start
game1 = game0

show(stdout, "text/plain", scoreboard) #full visualization of the scoreboard
#display(throwlog[:,347:362]) #debugging
#throwlog = [0, 0, 0, 0, 0] #log for debugging
scoreplotx = collect(1:300) #till line 22 for statistical analysis
scoreplotpropy = collect(1:300)
for i in 1:300
    scoreplotpropy[i] = count(==(i), scoreboard[21,2:200000])
end
plot(scoreplotx,scoreplotpropy, title = "Total Kniffel score distribution", label = "1 throw per round", xlabel = "Total score", ylabel = "Count")
maximum(scoreboard[21,2:200014])
minimum(scoreboard[21,2:200014])

#started 14:02

n = 1000000 #how many games would you like to play? choose value depending on width of REPL
for i in 1:n #till end
    game1[1] = i
    for t in 1:15 # =15 times rolling
        #throwing some dice...you allways have to start with a first throw #in this approach, first, one single throw (not 3) is getting realized
        throw1 = rand(1:6,5)
        throw1_count = [count(==(1), throw1), count(==(2), throw1), count(==(3), throw1), count(==(4), throw1), count(==(5), throw1), count(==(6), throw1)]
        #throwlog = hcat(throwlog, sort(throw1)) #just for debugging
        #2 sorting regarding multiplicity
        count1 = maximum(throw1_count)
        if count1 == 5 #kniffel
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            #println("kniffel of ",number,"s! - you are lucky")
            if game1[18] == -1 #enter points in game1
                game1[18] = 50
                #println("added a kniffel")
            elseif game1[18] == 0
                #println("kniffel got allready cancelled :(")
                if game1[number+1] == -1
                    game1[number+1] = sum(throw1)
                elseif game1[14] == -1
                    game1[14] = 4*number
                elseif game1[13] == -1
                    game1[13] = 3*number
                elseif game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[11] == -1
                    game1[11] = 2*number
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                elseif game1[2] == -1
                    game1[2] = 0
                elseif game1[3] == -1
                    game1[3] = 0
                elseif game1[4] == -1
                    game1[4] = 0
                elseif game1[5] == -1
                    game1[5] = 0
                elseif game1[6] == -1
                    game1[6] = 0
                elseif game1[7] == -1
                    game1[7] = 0
                end
            else
                game1[18] = game1[18] + 50
                #println("wow, another kniffel!")
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
                elseif game1[2] == -1
                    game1[2] = 0
                elseif game1[3] == -1
                    game1[3] = 0
                elseif game1[4] == -1
                    game1[4] = 0
                elseif game1[5] == -1
                    game1[5] = 0
                elseif game1[6] == -1
                    game1[6] = 0
                elseif game1[7] == -1
                    game1[7] = 0
                end
            end
        elseif count1 == 4 #quadruplet
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            leftovernumber = findfirst(x->x==1, throw1_count)
            #println("quadruplet with ",number,"s!")
            if game1[number+1] == -1 #enter points in game1
                game1[number+1] = 4*number
                #println("added a quadrupel")
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
                    game1[18] = 0
                elseif game1[17] == -1
                    game1[17] = 0
                elseif game1[15] == -1
                    game1[15] = 0
                elseif game1[12] == -1
                    game1[12] = 0
                elseif game1[16] == -1
                    game1[16] = 0
                elseif game1[1+leftovernumber] == -1
                    game1[1+leftovernumber] = leftovernumber
                elseif game1[2] == -1
                    game1[2] = 0
                elseif game1[3] == -1
                    game1[3] = 0
                elseif game1[4] == -1
                    game1[4] = 0
                elseif game1[5] == -1
                    game1[5] = 0
                elseif game1[6] == -1
                    game1[6] = 0
                elseif game1[7] == -1
                    game1[7] = 0
                end
            end
        elseif count1 == 3 #triplet, check for full house ##sadly these cases are not that clean: some parts are not necessary - however it works
            number = findfirst(x -> x == maximum(throw1_count), throw1_count)
            leftovernumbers = sort(findall(x->x==1, throw1_count)) #2 numbers, only the non full house case
            leftovernumber = findfirst(x->x==2, throw1_count) #1 number, only in the full house case
            missingnumbers = sort(findall(==(minimum(throw1_count)), throw1_count)) #3 or 4 numbers
            if count(==(0),throw1_count) == 4
                #println("full house!")
                if game1[15] == -1
                    game1[15] = 30
                    #println("added full house!")
                else
                    if game1[1+number] == -1
                        game1[1+number] = 3*number
                    elseif game1[13] == -1
                        game1[13] = number*3
                    elseif game1[11] == -1
                        if number < leftovernumber
                            game1[11] = 2*leftovernumber
                        else
                            game1[11] = 2*number
                        end
                    elseif game1[19] == -1
                        game1[19] = sum(throw1)
                    elseif game1[1+leftovernumber] == -1
                        game1[1+leftovernumber] = 2*leftovernumber
                    elseif length(leftovernumbers) == 2 && game1[1+leftovernumbers[1]] == -1
                        game1[1+leftovernumbers[1]] = leftovernumbers[1]
                    elseif length(leftovernumbers) == 2 && game1[1+leftovernumbers[2]] == -1
                        game1[1+leftovernumbers[2]] = leftovernumbers[2]
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
                    else
                        if length(missingnumbers) == 3
                            if game1[1+missingnumbers[1]] == -1
                                game1[1+missingnumbers[1]] = 0
                            elseif game1[1+missingnumbers[2]] == -1
                                game1[1+missingnumbers[2]] = 0
                            elseif game1[1+missingnumbers[3]] == -1
                                game1[1+missingnumbers[3]] = 0
                            end
                        elseif length(missingnumbers) == 4
                            if game1[1+missingnumbers[1]] == -1
                                game1[1+missingnumbers[1]] = 0
                            elseif game1[1+missingnumbers[2]] == -1
                                game1[1+missingnumbers[2]] = 0
                            elseif game1[1+missingnumbers[3]] == -1
                                game1[1+missingnumbers[3]] = 0
                            elseif game1[1+missingnumbers[4]] == -1
                                game1[1+missingnumbers[4]] = 0
                            end
                        end
                    end
                end
            else
                #println("triplet with ",number,"s!")
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
                elseif game1[1+leftovernumbers[1]] == -1
                    game1[1+leftovernumbers[1]] = leftovernumbers[1]
                elseif game1[1+leftovernumbers[2]] == -1
                    game1[1+leftovernumbers[2]] = leftovernumbers[2]
                elseif game1[1+missingnumbers[1]] == -1
                    game1[1+missingnumbers[1]] = 0
                elseif game1[1+missingnumbers[2]] == -1
                    game1[1+missingnumbers[2]] = 0
                elseif game1[1+missingnumbers[3]] == -1
                    game1[1+missingnumbers[3]] = 0
                end
            end
        elseif length(findall(x -> x == maximum(throw1_count), throw1_count)) == 2 #doublepair
            numbers = findall(x -> x == maximum(throw1_count), throw1_count)
            leftovernumber = findfirst(x->x==1, throw1_count)
            missingnumbers = sort(findall(==(minimum(throw1_count)), throw1_count)) #3 numbers
            #println("doublepair with ",numbers[1],"s and ",numbers[2],"s!")
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
            elseif game1[13] == -1
                game1[13] = 0
            elseif game1[1+leftovernumber] == -1
                game1[1+leftovernumber] = 1*leftovernumber
            elseif game1[1+missingnumbers[1]] == -1
                game1[1+missingnumbers[1]] = 0
            elseif game1[1+missingnumbers[2]] == -1
                game1[1+missingnumbers[2]] = 0
            elseif game1[1+missingnumbers[3]] == -1
                game1[1+missingnumbers[3]] = 0
            end
        elseif count1 == 2 #pair, check for street!
            number = findfirst(x -> x == maximum(throw1_count), throw1_count) #number of the pair
            missingnumbers = sort(findall(==(minimum(throw1_count)), throw1_count)) #2 missing numbers
            leftovernumbers = sort(findall(x->x==1, throw1_count)) # 3 numbers
            if 1 in missingnumbers && 2 in missingnumbers || 5 in missingnumbers && 6 in missingnumbers
                #println("pair of ",number,"s within a small street!")
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
                elseif game1[1+leftovernumbers[1]] == -1
                    game1[1+leftovernumbers[1]] = leftovernumbers[1]
                elseif game1[1+leftovernumbers[2]] == -1
                    game1[1+leftovernumbers[2]] = leftovernumbers[2]
                elseif game1[1+leftovernumbers[3]] == -1
                    game1[1+leftovernumbers[3]] = leftovernumbers[3]
                elseif game1[1+missingnumbers[1]] == -1
                    game1[1+missingnumbers[1]] = 0
                elseif game1[1+missingnumbers[2]] == -1
                    game1[1+missingnumbers[2]] = 0
                end
            elseif 1 in missingnumbers && 6 in missingnumbers
                #println("pair of ",number,"s within a small street, perfect go for big street")
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
                elseif game1[1+leftovernumbers[1]] == -1
                    game1[1+leftovernumbers[1]] = leftovernumbers[1]
                elseif game1[1+leftovernumbers[2]] == -1
                    game1[1+leftovernumbers[2]] = leftovernumbers[2]
                elseif game1[1+leftovernumbers[3]] == -1
                    game1[1+leftovernumbers[3]] = leftovernumbers[3]
                elseif game1[1+missingnumbers[1]] == -1
                    game1[1+missingnumbers[1]] = 0
                elseif game1[1+missingnumbers[2]] == -1
                    game1[1+missingnumbers[2]] = 0
                end
            else
                #println("just a pair of ",number,"s")
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
                elseif game1[1+leftovernumbers[1]] == -1
                    game1[1+leftovernumbers[1]] = leftovernumbers[1]
                elseif game1[1+leftovernumbers[2]] == -1
                    game1[1+leftovernumbers[2]] = leftovernumbers[2]
                elseif game1[1+leftovernumbers[3]] == -1
                    game1[1+leftovernumbers[3]] = leftovernumbers[3]
                elseif game1[1+missingnumbers[1]] == -1
                    game1[1+missingnumbers[1]] = 0
                elseif game1[1+missingnumbers[2]] == -1
                    game1[1+missingnumbers[2]] = 0
                end
            end
        elseif count1 == 1 #trash, street?
            missingnumber =  argmin(throw1_count)
            if missingnumber == 1 || missingnumber == 6
                #println("big street!")
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
                    elseif game1[2] == -1
                        game1[2] = 0
                    elseif game1[7] == -1
                        game1[7] = 0
                    end
                end
            elseif missingnumber == 2 || missingnumber == 5
                #println("small street!")
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
                    elseif game1[3] == -1
                        game1[3] = 0
                    elseif game1[6] == -1
                        game1[6] = 0
                    end
                end
            else
                #println("unlucky, that's a garbage throw")
                if game1[19] == -1
                    game1[19] = sum(throw1)
                elseif game1[2] == -1 && 1 in throw1
                    game1[2] = 1
                elseif game1[3] == -1 && 2 in throw1
                    game1[3] = 2
                elseif game1[4] == -1 && 3 in throw1
                    game1[4] = 3
                elseif game1[5] == -1 && 4 in throw1
                    game1[5] = 4
                elseif game1[6] == -1 && 5 in throw1
                    game1[6] = 5
                elseif game1[7] == -1 && 6 in throw1
                    game1[7] = 6
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
                elseif game1[2] == -1
                    game1[2] = 0
                elseif game1[3] == -1
                    game1[3] = 0
                elseif game1[4] == -1
                    game1[4] = 0
                elseif game1[5] == -1
                    game1[5] = 0
                elseif game1[6] == -1
                    game1[6] = 0
                elseif game1[7] == -1
                    game1[7] = 0
                end
            end
        end

        if t==15 #checking if game has finished yet
            #println("game ",i," finished!")
            game1[8] = sum(game1[2:7])
            if game1[8] >= 63
                game1[9] = 37
                game1[10] = game1[8] + game1[9]
            else
                game1[9] = 0
                game1[10] = game1[8]
            end
            game1[20] = sum(game1[11:19])
            game1[21] = game1[10] + game1[20]
            scoreboard = hcat(scoreboard,game1)
            println("added game ",i," to the scoreboard")
            game1 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        end
    end
end
