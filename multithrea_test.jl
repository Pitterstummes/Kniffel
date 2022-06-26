function firstthrow() #first throw: Output 5 element vector with numbers from 1 to 6
    firstthrow = sort(rand(1:6,5),rev=true)
    return firstthrow
end

Threads.nthreads()

@time firstthrow()