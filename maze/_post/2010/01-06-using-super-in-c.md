---
title: Using "super" in C++
---
My style of coding includes the following idiom:

    :::c++
    class Derived : public Base
    {
    private:
      typedef Base super;
      // etc...
    };

This enables me to use "super" as an alias to Base, for example, in constructors:

    :::c++
    Derived(int i, int j) : super(i), J(j)
    {
    }

Or even when calling the method from the base class inside its overriden
version:

    :::c++
    void Derived::doSomething()
    {
      super::doSomething() ;
      // etc...
    }

It can even be chained (I have still to find the use for that, though):

    :::c++
    class DerivedDerived : public Derived
    {
    public:
      typedef Derived super;
      // etc...
    };
     
    void DerivedDerived::doSomethingElse()
    {
      super::doSomethingElse() ; // will call Derived::doSomethingElse()
      super::super::doSomethingElse() ; // will call Base::doSomethingElse()
     
      // etc...
    }

Anyway, I find the use of "typedef super" very useful, for example, when Base is either verbose and/or templated.
