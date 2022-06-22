#Goals of this program are self contained playing of kniffel and also writing down into the analysis sheet + statistical analysis

#Initializing
scoreboard_start = ["Gamenumber", "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes", "Sum1", "Bonus", "Total 1", "Pair", "Doublepair", "Triplet",
 "Quadruplet", "Full House", "Small Street", "Big Street", "Kniffel", "Chance", "Total 2", "Total"] #21 entrys for left side legend
game0 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1] #reference: empty scoresheet (-1 means empty since 0 is needed for xed fields)
scoreboard = scoreboard_start #clear scoreboard
game = game0 #clear scoresheet

#Throwanalysis function: outputs a throwcase and number information
function throwanalysis(throw_count)
    counter = maximum(throw_count)
    #7 possible unique cases (total of 11 cases with subcases) -> 5 cases via counter
    if counter == 5 #case1: Kniffel
        number = findfirst(==(5), throw_count) #always 1 number
        missingnumber = sort(findall(==(0), throw_count)) #always 5 numbers !!DELAY this after checking for number - faster program!!
        throwcase = 1
        println("Kniffel") #break
        #continue working here
    elseif counter == 4 #case2: Quadruplet
        number = findfirst(==(4), throw_count) #always 1 number
        leftovernumber = findfirst(==(1), throw_count) #always 1 number !!DELAY this after checking for number - faster program!!
        missingnumber = sort(findall(==(0), throw_count)) #always 4 numbers !!DELAY this after checking for number - faster program!!
        throwcase = 2
        println("Quadruplet")
        #continue working here
    elseif counter == 3 #case3: Full House and case4: Triplet
        number = findfirst(==(3), throw_count) #always 1 number
        caseswitch = count(==(0), throw_count) # =4 if case3 and =3 if case4
        if caseswitch == 4 #case3: Full House
            leftovernumber = findfirst(==(2), throw_count) #always 1 number
            missingnumber = sort(findall(==(0), throw_count)) #always 4 numbers !!DELAY this after checking for number - faster program!!
            throwcase = 3
            println("Full House")
        elseif caseswitch == 3 #case4: Triplet
            leftovernumber = sort(findall(==(1), throw_count)) #always 2 numbers
            missingnumber = sort(findall(==(0), throw_count)) #always 3 numbers !!DELAY this after checking for number - faster program!!
            throwcase = 4
            println("Triplet")
        end
    elseif counter == 2 #case5: Doublepair and case6: Pair (contains subcases)
        caseswitch = count(==(2), throw_count) # =2 if case5 and =1 is case6
        if caseswitch == 2 #case5: Doublepair
            number = sort(findall(==(2), throw_count)) #always 2 numbers
            leftovernumber = findfirst(==(1), throw_count) #always 1 number
            missingnumber = sort(findall(==(0), throw_count)) #always 3 numbers !!DELAY this after checking for number - faster program!!
            throwcase = 5
            println("Doublepair")
        elseif caseswitch == 1 #case6: Pair (this case contains subcases 1-3, small street and good big street go, small street or just a pair)
            number = findfirst(==(2), throw_count) #always 1 number
            leftovernumber = sort(findall(==(1), throw_count)) #always 3 numbers
            missingnumber = sort(findall(==(0), throw_count)) #always 2 numbers !!DELAY this after checking for number - faster program!!
            if 1 in missingnumber && 6 in missingnumber #go for Big Street
                throwcase = 6.1
                println("Pair + Small Street with good Big Street go")
            elseif 1 in missingnumber && 2 in missingnumber || 5 in missingnumber && 6 in missingnumber # Small Street
                throwcase = 6.2
                println("Pair + Small Street")
            else
                throwcase = 6.3
                println("Pair")
            end
        end
    elseif counter == 1 #case7: 3 subcases, Big street, small street or nothing
        missingnumber = findfirst(==(0), throw_count) #always 1 number
        number = sort(findall(==(1), throw_count)) #always 5 numbers !!DELAY this after checking for number - faster program!!
        if missingnumber == 1 || missingnumber == 6
            throwcase = 7.1
            println("Big Street")
        elseif missingnumber == 2 || missingnumber == 5
            throwcase = 7.2
            println("Small Street")
        else
            throwcase = 7.3
            println("Nothing")
        end
    end
end

#registercheck, input is output of throwanalysis
leftgames = []
for j in 1:15 #all 15 cases
    if j<7 #projecting j to the actucal case number c
        c = j+1
    else
        c = j+4
    end
    if game[c] == -1
        leftgames = append!(leftgames,c)
    end
end
#possibilities after registerckeck depending on throwcase
kniffel -> write down points and do a break for the 3 throw loop - if relevant slots are not aviable -> rerolling ...........


keepdice = [1,2,3,4,5]

#give throwdice val
if throwcase == 1 #Kniffel
    keepdice = [number, number, number, number, number]
    if game[18] == -1
        game[18] = 50
    elseif game[18] == 0
        -----------------------------------------------
elseif throwcase == 2 #Quadruplet
    throwdice = 1
elseif throwcase == 3 #Full House
    #look at the different cases regarding space in the scorelist
elseif throwcase == 4 #Triplet
    throwdice = 2
elseif throwcase == 5 #Doublepair
    #look at the different cases regarding space in the scorelist
elseif throwcase == 6.1 #go for Big Street (already small street)
    #look at the different cases regarding space in the scorelist
elseif throwcase == 6.2 #Small Street + Pair
    #look at the different cases regarding space in the scorelist
elseif throwcase == 6.3 #Pair
    #look at the different cases regarding space in the scorelist
elseif throwcase == 7.1 #Big Street
    if game[17] == -1
        game[17] = 40
        break
    elseif game[16] == -1
        game[16] = 25
        break
    elseif 6 in number && game[7] == -1 && game[11] == -1 || 6 in number && game[7] == -1 && game[19] == -1
        throwdice = 4
    else..........................................................................
    end

    #look at the different cases regarding space in the scorelist
elseif throwcase == 7.2
    #look at the different cases regarding space in the scorelist
elseif throwcase == 7.3
    #look at the different cases regarding space in the scorelist
end
throwdice = 5-length(keepdice)

#append dicetrow random numbers to the kept throw -> still have to implement the keepdice mechanic
throw = append!(keepdice,throw)


#Visualization of Scoreboard
function showboard(g)
    show(stdout, "text/plain", hcat(scoreboard[:,1],scoreboard[:,g+1]))
end
show(stdout, "text/plain", leftgames)
showboard(5) #shows the scoreboard at gamenumber = functionposition

#Runparameters
numberofgames = 1 #how many games would you like to play?
totalthrows = 3 # throws per round, normally=3: which sick bastard would not abide by the normal rules, however any number is possible (hopefully)

for i in 1:numberofgames #till end
    game[1] = i #write gamenumber in scoresheet
    for r in 1:1 # 15 fields to fill per game, r stands for round, do not change
        throwdice = 5
        for t in 1:totalthrows #typical 3, end of this loop is writing a score into the scoresheet
            if throwdice != 0 #exits when dice are already optimal
                throw = rand(1:6,throwdice)
                println(throw)
                throw_count = [count(==(1), throw), count(==(2), throw), count(==(3), throw), count(==(4), throw), count(==(5), throw), count(==(6), throw)]
                throwanalysis(throw_count)
                #modifying throwdice depending on cases
            else
                println("writing into the scorelist")
            end
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
